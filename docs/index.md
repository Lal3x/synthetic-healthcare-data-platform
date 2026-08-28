# Synthetic Healthcare Data Platform

Este projeto demonstra um pipeline de dados clínicos sintéticos construído com
Python, Airflow, PostgreSQL e Streamlit. O processamento segue a arquitetura
Bronze, Silver e Gold e produz indicadores executivos de pacientes e atendimentos.

## Objetivo

O objetivo do projeto é mostrar, de forma didática, como:

- organizar arquivos em formato CSV;
- carregar dados em um banco relacional;
- transformar esses dados em camadas de processamento;
- aplicar consultas analíticas para obter insights;
- aplicar uma arquitetura de dados em Bronze, Silver e Gold;
- orquestrar e observar cada etapa pelo Airflow;
- apresentar os resultados em um painel Streamlit.

## Contexto

A ideia central é representar um fluxo realista e reproduzível em um ambiente
local conteinerizado. Os dados são sintéticos e o projeto tem finalidade
educacional, sem uso para decisões médicas.

## Tecnologias utilizadas

- Python: manipulação dos dados, leitura de CSV, transformação e execução do pipeline.
- SQL: criação de schemas, criação de tabelas e consultas analíticas.
- PostgreSQL: banco de dados relacional utilizado como camada de armazenamento.
- SQLAlchemy: integração entre Python e banco de dados.
- Pandas: processamento tabular dos dados.
- pytest e pytest-cov: testes automatizados e cobertura.
- Black, Ruff e Taskipy: padronização, linting e automação de tarefas.
- MkDocs Material: documentação do projeto.
- Apache Airflow: orquestração e observabilidade das tarefas.
- Streamlit e Plotly: painel executivo dos indicadores.
- Docker Compose: execução integrada dos serviços e bancos PostgreSQL.

## Arquitetura em camadas

O fluxo de processamento do projeto segue o modelo medalhão:

1. Bronze: dados brutos e originados em CSV.
2. Silver: dados limpos, normalizados e validados.
3. Gold: agregações e tabelas analíticas prontas para consumo.

Esse padrão ajuda a separar dados crus de dados prontos para análise e facilita a manutenção e auditoria do pipeline.

## Casos de uso

- Validação de qualidade dos dados carregados.
- Transformação de dados clínicos e demográficos.
- Agregação de métricas por paciente, encontro e condição.
- Estudo de comportamento e indicadores em dados sintéticos de saúde.

## Próximos passos

- expandir o volume de dados e cenários;
- adicionar mais consultas SQL analíticas;
- ampliar a cobertura dos módulos de integração com PostgreSQL;
- incluir monitoramento e alertas para falhas da DAG.
