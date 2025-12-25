# 🕵️ Agente de IA Forense & Analista SQL (v2.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![Ollama](https://img.shields.io/badge/Model-Llama3-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

> Um agente autônomo local capaz de realizar investigações forenses em transações bancárias (PIX/SPB) e converter perguntas em linguagem natural para SQL seguro (**Text-to-SQL**).

---

## 🚀 Novidades da Versão 2.0
Esta versão introduz uma arquitetura híbrida para otimização de custos e performance:

* **⚡ Extração Híbrida (Regex + IA):** Implementação de *parsers* Regex para mineração imediata de tags de erro em XMLs brutos (`<AddtlInf>`, `<RsnDesc>`), eliminando a necessidade de enviar payloads gigantes para o LLM.
* **🛡️ Text-to-SQL Blindado:** Nova camada de *Prompt Engineering* defensivo que previne alucinações de tipagem (ex: forçar tratamento de Inteiros vs Strings no banco).
* **⏱️ Cálculo de SLA em Tempo Real:** O agente agora calcula a latência de processamento (`delta` entre entrega e consumo) e alerta automaticamente sobre gargalos de performance (> 10s).
* **🔍 Visão Unificada (Real-time + Legacy):** Algoritmo de busca que cruza dados de tabelas transacionais (`.operacao`) e históricas (`.legado`) em uma única view investigativa.

---

## ⚙️ Arquitetura

O sistema opera em dois modos distintos, detectados automaticamente pela entrada do usuário:

### 1. Modo Investigador (Detecção de NUOP)
Se a entrada for um ID de transação (NUOP), o sistema:
1.  **Rastreia** o ciclo de vida da mensagem em 3 tabelas diferentes (SPI, SPB, Legado).
2.  **Analisa** os logs XML usando Regex para encontrar a causa raiz de falhas.
3.  **Gera** um relatório em Markdown com cronologia e Veredito da IA.

### 2. Modo Analista (Text-to-SQL)
Se a entrada for uma pergunta (ex: *"Quais erros de PIX tivemos hoje?"*), o sistema:
1.  **Injeta** o esquema do banco de dados no contexto do Llama 3.
2.  **Gera** uma query SQL sintaticamente correta (PostgreSQL).
3.  **Sanitiza** a query e a executa em modo leitura.
4.  **Exibe** os resultados tabulados.

---

## 🛠️ Stack Tecnológico

* **Core:** Python 3.10+, Pandas, Psycopg2
* **IA & Orquestração:** LangChain, Ollama (Llama 3 Local)
* **Database:** PostgreSQL
* **Utilities:** Regex (Re), Dotenv

---

## 📦 Instalação e Uso

### Pré-requisitos
* Python instalado.
* [Ollama](https://ollama.com/) rodando localmente com o modelo Llama 3 (`ollama run llama3`).
* Banco de Dados PostgreSQL acessível.

### 1. Clone o repositório

git clone [https://github.com/seu-usuario/agente-ia-forense.git](https://github.com/seu-usuario/agente-ia-forense.git)
cd agente-ia-forense

2. Configure o Ambiente
Crie um arquivo .env na raiz do projeto (use o .env.example como base):

# Configurações do Banco de Dados
DB_HOST=x.x.x.x
DB_PORT=xxxx
DB_NAME=nome_do_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha


# Configuração da IA (Ollama Local)
OLLAMA_BASE_URL=http://localhost:11434

3. Instale as Dependências
Recomenda-se usar um ambiente virtual (venv):

# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt

4. Execute o Agente
bash
python main.py

🧠 Exemplos de Uso
O sistema identifica automaticamente o que você deseja fazer:

🕵️ Modo Investigação (Cole um ID)
Ideal para descobrir por que uma transação falhou.

Entrada:

E90400888202407091400... (ID do PIX/NUOP)

Saída:

🔍 Rastreamento: Localiza a operação na tabela spi.legado.

⚡ SLA: "Tempo de consumo: 0.4s (Rápido)".

❌ Erro: Extrai do XML: <RsnDesc>Saldo Insuficiente</RsnDesc>.

📄 Arquivo: Gera relatorio_E904...md.

📊 Modo Analista (Faça uma pergunta)
Ideal para relatórios rápidos sem escrever SQL.

Entrada:

"Me mostre as últimas 5 transações rejeitadas pelo Bacen hoje"

Saída:

🤖 O Agente gera o SQL:

SQL

SELECT * FROM spi.operacao WHERE statusop = 205 ORDER BY ts_inclusao DESC LIMIT 5;
📊 Exibe a tabela de resultados no terminal.

📂 Estrutura do Projeto
Plaintext

.
├── main.py            # Orquestrador Principal (IA + SQL + Regex)
├── requirements.txt   # Dependências do Python
├── .env               # Variáveis de Ambiente (Configuração)
└── README.md          # Documentação
🔒 Segurança & Privacidade
Zero Data Leak: Todo o processamento de IA é feito localmente via Ollama. Nenhum dado bancário sensível é enviado para nuvens públicas (OpenAI/Google).

Read-Only: O agente é configurado para executar apenas comandos de leitura (SELECT), garantindo a integridade do banco de dados.

Autor
Desenvolvido por Vinicius Costa
