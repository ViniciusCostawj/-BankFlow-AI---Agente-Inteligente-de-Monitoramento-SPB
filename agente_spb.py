import os
import pandas as pd
import psycopg2
import warnings
import re
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 0. CONFIGURAÇÃO GERAL ---
warnings.filterwarnings('ignore')
load_dotenv()

# --- 1. CONFIGURAÇÃO DO BANCO (via .env) ---
# Valores são lidos a partir das variáveis de ambiente. Preencha .env localmente.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", ),
    "port": os.getenv("DB_PORT", ),
    "database": os.getenv("DB_NAME", ),
    "user": os.getenv("DB_USER", ),
    "password": os.getenv("DB_PASSWORD", )
}

TABELAS_DETALHE = ["spb.operacao", "consolid.operacao", "consolid02.operacao"]

# --- 2. MAPA DE STATUS ---
MAPA_STATUS = {
    100: "ENVIO_PILOTO", 106: "ENVIO_SUCESSO", 204: "RECEBTO_SUCESSO", 205: "ERRO_BACEN",
    301: "PROCESSANDO", 302: "OK", 306: "INFORMATIVO", 307: "AVISO", 
    313: "AGUARD_LIB_AUTORIZ", 320: "REJ_AUTORIZADOR",
    324: "PIX_AUTO_NAO_CONTRATADO"
}

# --- 3. CONEXÃO IA ---
print("🔌 Conectando ao Llama 3 local...")
try:
    llm = ChatOllama(model="llama3", temperature=0, base_url="http://localhost:11434")
except Exception as e:
    print(f"❌ Erro ao conectar no Ollama: {e}")
    exit()

# --- 4. TRADUTOR SQL (V8 - CORREÇÃO DE LÓGICA RÍGIDA) ---
# Mudança: Ensinamos a ele a diferenciar quando o usuário pede um NÚMERO vs um TIPO genérico.
template_sql = """
Você é um Gerador SQL. Retorne APENAS o SQL.

MAPA DE TABELAS:
1. 'spb.operacao' -> HOJE, "últimas", "agora".
2. 'consolid.operacao' -> ONTEM, "histórico".

REGRAS DE FILTRO (ATENÇÃO):
1. Se o usuário pedir um NÚMERO ESPECÍFICO (ex: "status 313"), use APENAS esse número no WHERE.
   - Se o número for > 300 -> WHERE statusmsg = X
   - Se o número for < 300 -> WHERE statusop = X
   
2. Se o usuário NÃO der número (ex: "mostre os erros"), aí sim use listas:
   - Erros -> statusmsg IN (303, 308, 320) OR statusop IN (205, 107)

3. COLUNAS OBRIGATÓRIAS:
   SELECT msgid, TRIM(nuop) as nuop, statusop, statusmsg, ts_inclusao, codmsg

PERGUNTA: {pergunta}
SQL:
"""
prompt_sql = PromptTemplate(input_variables=["pergunta"], template=template_sql)
chain_sql = prompt_sql | llm | StrOutputParser()

def buscar_inteligente(pergunta):
    print(f"\n🧠 Gerando SQL para: '{pergunta}'...")
    
    sql_bruto = chain_sql.invoke({"pergunta": pergunta})
    
    # --- LIMPEZA BLINDADA ---
    sql_limpo = re.sub(r"```sql|```", "", sql_bruto).strip()
    
    # Corta antes do SELECT
    inicio = sql_limpo.upper().find("SELECT")
    if inicio != -1:
        sql_limpo = sql_limpo[inicio:]
    
    # Corta depois do ponto e vírgula
    fim = sql_limpo.find(";")
    if fim != -1:
        sql_limpo = sql_limpo[:fim+1]
    
    print(f"💻 SQL Executado: {sql_limpo}")
    
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(sql_limpo, conn)
        return df
    except Exception as e:
        print(f"❌ Erro SQL: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# --- 5. INVESTIGADOR DE FLUXO ---
def analisar_nuop_detalhado(nuop_alvo):
    print(f"\n🕵️ Investigando NUOP: {nuop_alvo}...")
    conn = psycopg2.connect(**DB_CONFIG)
    dfs = []
    try:
        for tabela in TABELAS_DETALHE:
            query = f"""
                SELECT '{tabela}' as origem, msgid, TRIM(nuop) as nuop, 
                       codmsg, statusop, statusmsg, ts_inclusao as hora
                FROM {tabela} WHERE nuop LIKE '%{nuop_alvo.strip()}%'
                ORDER BY ts_inclusao ASC
            """
            try:
                df_temp = pd.read_sql(query, conn)
                if not df_temp.empty: dfs.append(df_temp)
            except: pass
        
        if not dfs: return pd.DataFrame()
        
        df_final = pd.concat(dfs).sort_values(by='hora')
        
        def traduzir_linha(row):
            desc_op = MAPA_STATUS.get(row['statusop'], str(row['statusop']))
            desc_msg = MAPA_STATUS.get(row['statusmsg'], "") if pd.notnull(row['statusmsg']) and row['statusmsg'] > 0 else ""
            if desc_msg: return f"{desc_op} ({desc_msg})"
            return desc_op

        df_final['descricao'] = df_final.apply(traduzir_linha, axis=1)
        return df_final
    finally:
        conn.close()

# --- 6. RELATÓRIO ---
template_analise = """
Você é Analista N3. Analise o fluxo do NUOP {nuop}.
DADOS: {tabela_dados}
Responda: 1. Resumo cronológico. 2. Veredito.
"""
chain_analise = PromptTemplate(input_variables=["nuop", "tabela_dados"], template=template_analise) | llm | StrOutputParser()

def salvar_relatorio(nuop, df, analise):
    diag = "```mermaid\ngraph TD;\n" + " --> ".join([f"s{i}[{r['hora'].strftime('%H:%M:%S')}<br>{r['descricao']}]" for i, r in df.iterrows()]) + "\n```"
    with open(f"relatorio_{nuop.strip()}.md", "w", encoding="utf-8") as f: 
        f.write(f"# Relatório {nuop}\n\n## Visual\n{diag}\n\n## IA\n{analise}\n\n## Dados\n{df.to_markdown(index=False)}")
    print(f"\n💾 Relatório salvo!")

# --- 7. MAIN ---
def main():
    while True:
        entrada = input("\n🎯 Pergunta ou NUOP (ou 'sair'): ").strip()
        if entrada.lower() in ['sair', 'exit']: break
        if not entrada: continue

        if " " in entrada:
            df = buscar_inteligente(entrada)
            if not df.empty:
                print(f"\n✅ Encontrei {len(df)} registros:")
                cols = [c for c in df.columns if c in ['nuop', 'statusop', 'statusmsg', 'ts_inclusao', 'codmsg']]
                print(df[cols].to_markdown(index=False))
                
                if 'nuop' in df.columns:
                    sel = input("\n🔎 Copie um NUOP para ver o gráfico (ou Enter): ").strip()
                    if sel:
                        dff = analisar_nuop_detalhado(sel)
                        if not dff.empty:
                            ana = chain_analise.invoke({"nuop": sel, "tabela_dados": dff.to_markdown()})
                            print(f"\n🤖 {ana}")
                            salvar_relatorio(sel, dff, ana)
            else:
                print("⚠️ Nada encontrado.")
        else:
            nuop = entrada.replace("'", "").replace('"', "")
            dff = analisar_nuop_detalhado(nuop)
            if not dff.empty:
                ana = chain_analise.invoke({"nuop": nuop, "tabela_dados": dff.to_markdown()})
                print(f"\n🤖 {ana}")
                salvar_relatorio(nuop, dff, ana)
            else:
                print("⚠️ NUOP não encontrado.")

if __name__ == "__main__":
    main()