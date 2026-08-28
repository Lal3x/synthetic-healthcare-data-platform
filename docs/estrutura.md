# Estrutura do Projeto

A estrutura do repositório foi organizada para separar responsabilidades e facilitar a manutenção do pipeline.

```text
healthcare_analytics/
├── .env                    # variáveis de ambiente locais
├── .env.example            # modelo seguro de configuração
├── .dockerignore           # exclusões do contexto das imagens
├── .gitignore              # proteção de arquivos sensíveis e locais
├── .python-version         # versão do Python do projeto
├── .github/
│   ├── dependabot.yml      # atualizações automáticas de dependências
│   └── workflows/
│       ├── ci.yml          # qualidade, testes e build Docker
│       └── docs.yml        # publicação no GitHub Pages
├── README.md               # resumo rápido do projeto
├── docker-compose.yml      # serviços locais integrados
├── Dockerfile.airflow      # imagem do Airflow com dependências do projeto
├── Dockerfile.streamlit    # imagem do painel executivo
├── app/
│   └── streamlit_app.py    # interface de indicadores
├── dags/
│   └── healthcare_pipeline.py # orquestração no Airflow
├── mkdocs.yml              # configuração do MkDocs Material
├── pyproject.toml          # dependências e configuração do projeto
├── config/airflow/         # configurações avançadas opcionais
├── plugins/                # extensões opcionais do Airflow
├── data/raw/               # CSVs locais não versionados
├── logs/airflow/           # logs locais não versionados
├── notebooks/              # notebooks de análise e validação
├── sql/
│   └── ddl/                # script SQL de criação dos schemas
├── src/
│   └── healthcare_analytics/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── reset_db.py
│       ├── bronze/
│       │   ├── ingest.py
│       │   └── readers.py
│       ├── silver/
│       │   ├── transform.py
│       │   └── transformations.py
│       ├── gold/
│       │   ├── aggregate.py
│       │   └── aggregations.py
│       ├── config/
│       │   └── settings.py
│       └── utils/
│           ├── db.py
│           └── schema.py
├── tests/
│   ├── __init__.py
│   └── unit/
│       ├── conftest.py
│       ├── test_bronze_readers.py
│       ├── test_database_utils.py
│       ├── test_gold_aggregations.py
│       ├── test_layer_loaders.py
│       ├── test_main.py
│       ├── test_reset_db.py
│       ├── test_settings.py
│       └── test_silver_transformations.py
└── docs/
    ├── index.md
    ├── arquitetura.md
    ├── estrutura.md
    ├── instalacao.md
    ├── pipeline.md
    └── testes.md
```

## Padrão de organização

### `src/healthcare_analytics`

Contém os módulos da aplicação, separados por camada funcional:

- `bronze`: ingestão e leitura dos dados brutos;
- `silver`: limpeza, validação e transformações;
- `gold`: agregações e tabelas finais;
- `config`: leitura de configurações e variáveis de ambiente;
- `utils`: utilitários de conexão ao banco e criação de schemas.

### `sql`

Script SQL usado para criar os schemas Bronze, Silver e Gold.

### `tests`

Testes automatizados de leitura, configuração, utilitários, orquestração,
transformações e agregações.

### `docs`

Documentação técnica e conceitual do projeto com MkDocs Material.

### `config/airflow` e `plugins`

Pastas opcionais montadas no Airflow para futuras configurações avançadas e
extensões. O funcionamento atual não depende de arquivos dentro delas.

### `.github`

Centraliza integração contínua, validação Docker, publicação da documentação e
atualização automática de dependências.
