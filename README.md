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
```bash
git clone [https://github.com/seu-usuario/agente-ia-forense.git](https://github.com/seu-usuario/agente-ia-forense.git)
cd agente-ia-forense
