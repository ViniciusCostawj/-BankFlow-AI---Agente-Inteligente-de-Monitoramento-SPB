🏦 BankFlow AI - Agente Inteligente de Monitoramento SPB
AIOps (Artificial Intelligence for IT Operations) aplicado ao monitoramento de transações bancárias do Sistema de Pagamentos Brasileiro (SPB).

Este projeto é um Agente Autônomo capaz de investigar incidentes em bancos de dados transacionais usando Linguagem Natural. Ele combina a capacidade de raciocínio do Llama 3 com a precisão de queries SQL no PostgreSQL para diagnosticar falhas, rastrear mensagens e gerar relatórios visuais.

🚀 Funcionalidades Principais
🗣️ Busca Natural (Text-to-SQL): Permite que o operador faça perguntas em português (ex: "Quais mensagens foram rejeitadas pelo autorizador hoje?") e converte automaticamente para SQL seguro e otimizado.

🧠 Roteamento Temporal Inteligente: O agente entende o contexto de tempo e decide automaticamente qual tabela consultar:

spb.operacao para dados em tempo real (D0).

consolid.operacao para dados históricos (D-1+).

🕵️ Deep Dive Analysis: Ao receber um ID de transação (NUOP), o agente varre múltiplos schemas, reconstrói a linha do tempo e identifica gargalos.

📊 Visualização Automática: Gera diagramas de fluxo (Mermaid) para facilitar a leitura de logs técnicos por humanos.

🛡️ SQL Sanitization: Camada de segurança que limpa e valida os comandos gerados pela IA antes da execução no banco.

🛠️ Stack Tecnológica
Linguagem: Python 3.12

IA / LLM: Llama 3 (via Ollama - Execução 100% Local/Privada)

Orquestração: LangChain

Banco de Dados: PostgreSQL (Lib: psycopg2)

Manipulação de Dados: Pandas

⚙️ Como Funciona a Arquitetura
Entrada: O usuário digita uma pergunta ou um NUOP.

Classificação: O script detecta se é uma busca natural ou um rastreio específico.

Geração de SQL: Se for busca, o Llama 3 gera a query baseada no schema do banco e nas regras de negócio (diferenciando statusop de statusmsg).

Execução: O Python conecta no Postgres, roda a query e recupera os dados brutos.

Análise Semântica: O Llama 3 analisa os logs retornados, traduz códigos de erro (ex: 320 -> Rejeição) e emite um veredito.

Report: Um arquivo .md é gerado contendo a análise textual e o gráfico visual.

📸 Exemplos de Uso
1. Busca Inteligente (Natural Language)
Usuário: "Me mostre as últimas 5 mensagens com erro 313" Agente:

SQL

-- SQL Gerado Automaticamente pela IA
SELECT msgid, TRIM(nuop) as nuop, statusop, statusmsg, ts_inclusao 
FROM spb.operacao 
WHERE statusmsg = 313 
ORDER BY ts_inclusao DESC LIMIT 5;
2. Análise de Fluxo (NUOP)
Usuário: 00038166202512126005171 Agente: "Localizei o fluxo. A mensagem entrou pelo APP, foi processada, mas rejeitada pelo Autorizador (Status 320). Relatório visual salvo."

📝 Exemplo de Relatório Gerado
O sistema cria automaticamente arquivos Markdown com diagramas renderizáveis no GitHub/VS Code:

Snippet de código

graph TD;
    s0[10:34:22<br>RECEBTO_SUCESSO] --> s1[10:34:25<br>PROCESSANDO]
    s1 --> s2[10:34:28<br>REJ_AUTORIZADOR (320)]
📦 Instalação e Configuração
Pré-requisitos
Python 3.10+ instalado.

Ollama instalado e rodando localmente.

Acesso a um banco PostgreSQL.

Passo a Passo
Clone o repositório:

Bash

git clone https://github.com/seu-usuario/bankflow-ai.git
cd bankflow-ai
Instale as dependências:

Bash

pip install pandas psycopg2 langchain-ollama
Baixe o modelo Llama 3 no Ollama:

Bash

ollama run llama3
Configure as credenciais do banco no arquivo agente_spb.py:

Python

DB_CONFIG = {
    "host": "SEU_IP",
    "database": "SEU_DB",
    "user": "SEU_USER",
    "password": "SEU_PASSWORD"
}
Execute o agente:

Bash

python agente_spb.py
⚠️ Nota de Segurança
Este projeto foi desenhado para rodar com LLMs Locais (Ollama). Isso garante que nenhum dado bancário sensível (CPFs, Valores, Contas) seja enviado para APIs externas (como OpenAI ou Anthropic), mantendo a conformidade com normas de segurança bancária e LGPD.

👨‍💻 Autor
Desenvolvido por [Seu Nome] Especialista em Monitoramento e Automação de Sistemas Bancários.****
