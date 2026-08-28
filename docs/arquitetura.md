# Visão Geral da Arquitetura

A arquitetura do projeto foi pensada para simular um fluxo de dados em camadas, de forma simples e didática.

## Fluxo do pipeline

```text
CSV / dados brutos
        ↓
     Airflow
        ↓
   Bronze
        ↓
   Silver
        ↓
   Gold
        ↓
    Streamlit
```

## Serviços Docker

- `postgres-app`: armazena os dados das camadas Bronze, Silver e Gold;
- `postgres-airflow`: armazena os metadados da orquestração;
- `airflow-api-server`: fornece a interface web e a API de execução;
- `airflow-scheduler`: agenda e envia tarefas para execução;
- `airflow-dag-processor`: interpreta os arquivos de DAG;
- `airflow-triggerer`: processa tarefas assíncronas;
- `streamlit`: apresenta os indicadores consolidados.

Os serviços do Airflow compartilham a mesma URL da API e a mesma chave JWT. As
pastas `dags`, `src`, `data`, `sql`, `logs`, `config` e `plugins` são montadas nos
containers conforme sua responsabilidade.

`config/airflow` e `plugins` são pontos de extensão opcionais. No estado atual,
as configurações obrigatórias são fornecidas por variáveis de ambiente no Compose.

## Bancos de dados

O projeto mantém duas instâncias isoladas:

- o banco da aplicação recebe as camadas Bronze, Silver e Gold;
- o banco do Airflow guarda DAG runs, tarefas, usuários e demais metadados.

Essa separação impede que metadados da orquestração se misturem aos dados do
pipeline.

## Camada Bronze

A camada bronze é responsável por receber os dados em formato CSV e carregá-los praticamente da forma como chegam. Nesta etapa:

- os arquivos são lidos em Python;
- as colunas são normalizadas;
- metadados de execução são adicionados;
- os dados são persistidos em tabelas de origem.

Objetivo: preservar os dados originais sem perder contexto.

## Camada Silver

A camada silver realiza etapa de limpeza e padronização. O principal foco é:

- validar a qualidade dos dados;
- remover inconsistências;
- transformar colunas e campos;
- separar e organizar informações relevantes para análise.

Essa etapa produz tabelas mais confiáveis para uso analítico.

## Camada Gold

A camada gold é a parte analítica do pipeline. Nesta etapa são criadas:

- tabelas agregadas por paciente;
- resumos por tipo de encontro;
- uma visão conjunta dos dados para análise exploratória.

Essas tabelas são mais adequadas para consultas e relatórios.

## Benefícios do modelo

- organização clara do processamento;
- facilidade de depuração por etapa;
- rastreabilidade das transformações;
- melhor qualidade dos dados para uso analítico.

## Observações

Esse projeto não busca reproduzir uma plataforma completa de dados em produção. A proposta é demonstrar, de maneira acessível, o pensamento de pipeline de dados em camadas usando tecnologias simples e eficientes.

O Streamlit consulta somente os resultados já consolidados. Ele não executa a DAG
e não precisa de uma DAG própria.

## Qualidade e segurança

O GitHub Actions executa testes, lint e validação das imagens. O Dependabot
acompanha atualizações de Python, Docker e das próprias Actions. SAST com CodeQL
pode ser habilitado futuramente se o repositório se tornar público ou passar a
utilizar GitHub Code Security. O DAST também permanece como evolução futura.
