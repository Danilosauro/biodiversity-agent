# Biodiversity Agent

Sistema agentic para análise, transformação e avaliação da qualidade de dados de biodiversidade, com foco na interoperabilidade com o padrão **Darwin Core**.

## 1. Explicação do projeto

O **Biodiversity Agent** é uma solução para transformar dados de observações de biodiversidade em um formato estruturado e interoperável segundo o **Darwin Core**.

O projeto combina um **LLM local** com processamento determinístico em Python para realizar:

- análise semântica dos dados;
- planejamento dos mapeamentos;
- transformação e normalização dos dados;
- conversão para Darwin Core;
- validação;
- avaliação da qualidade dos dados;
- geração de evidências e artefatos do processamento.

A arquitetura foi desenvolvida para evitar que o LLM execute diretamente operações críticas sobre os dados.

---

## 2. Papel do LLM no projeto

O LLM, utilizando **Llama 3.2 via Ollama**, atua como uma camada de **interpretação e planejamento**.

Ele analisa as colunas e uma amostra dos dados para identificar:

- objetivo provável do dataset;
- correspondência entre campos de origem e termos Darwin Core;
- transformações necessárias;
- possíveis ambiguidades;
- operações de limpeza;
- validações recomendadas.

O LLM **não executa diretamente as transformações** e não é responsável pela validação final.

As operações críticas são executadas por funções determinísticas em Python, reduzindo riscos de:

- informações inventadas;
- mapeamentos inconsistentes;
- transformações incorretas;
- validações omitidas.

---

## 3. Funcionamento

O pipeline segue o fluxo:


Dataset CSV
     ↓
Bronze
     ↓
Profiling
     ↓
LLM — análise e planejamento
     ↓
Agent Plan
     ↓
Silver — transformações determinísticas
     ↓
Darwin Core Gold
     ↓
Validação
     ↓
Métricas de qualidade
     ↓
Dashboard / Relatórios´



## 4. Como usar 

Instale as bibliotecas necessárias:

- pip install -r requirements.txt 
- ollama pull llama3.2
- python main.py


Os principais resultados são gerados em : 

- data/bronze/
- data/silver/
- data/gold/
- logs/
- reports/


Após a execução do pipeline, rode o seguinte comando: 

- streamlit run app/streamlit_app.py

para visualização de um report contendo informações acerca da qualidade dos dados.


## 5. Escalabilidade

A arquitetura foi organizada para permitir a evolução do protótipo para diferentes datasets, domínios e padrões de interoperabilidade.

A separação entre LLM e processamento determinístico permite substituir ou expandir componentes individualmente.

Possíveis extensões incluem:

novos datasets de biodiversidade;
novos termos e extensões Darwin Core;
novos modelos de linguagem;
integração com APIs e bancos de dados;
processamento de grandes volumes de dados;
execução distribuída;
novos agentes especializados;
inclusão de outras etapas de análise ecológica.

O princípio central é manter o LLM responsável pela interpretação e planejamento, enquanto as operações críticas permanecem determinísticas, testáveis e auditáveis.
