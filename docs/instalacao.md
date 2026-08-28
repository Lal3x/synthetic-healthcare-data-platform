# Instalação e Execução

## Requisitos

- Python 3.13
- Poetry
- Docker com Docker Compose
- Arquivos CSV de entrada no diretório de dados

## Clonando o projeto

```bash
git clone <url-do-repositorio>
cd healthcare_analytics
```

## Criando o ambiente virtual

```bash
poetry install
```

O Poetry é necessário para desenvolvimento, testes e execução local. Os serviços
Docker instalam suas próprias dependências nas imagens.

## Configurando variáveis de ambiente

Copie o arquivo de exemplo e ajuste as credenciais se necessário:

```bash
cp .env.example .env
```

Por padrão, a aplicação usa o PostgreSQL exposto na porta `5432`:

```env
DATABASE_URL=postgresql://healthcare_analytics:healthcare_analytics@localhost:5432/healthcare_analytics
APP_ENV=dev
LOG_LEVEL=INFO
SCHEMA_BRONZE=bronze
SCHEMA_SILVER=silver
SCHEMA_GOLD=gold
RAW_DATA_DIR=data/raw
```

Essa `DATABASE_URL` é usada por comandos executados no host. Dentro dos
containers, o Compose substitui o endereço por `postgres-app`, nome interno do
serviço na rede Docker.

Gere uma chave para a autenticação interna do Airflow e coloque o resultado em
`AIRFLOW_JWT_SECRET` no `.env`:

```bash
openssl rand -hex 64
```

Em Linux, também é recomendável definir `AIRFLOW_UID` com o valor retornado por:

```bash
id -u
```

Isso evita que os logs locais sejam criados com outro proprietário.

Os arquivos `patients.csv`, `encounters.csv` e `conditions.csv` devem estar em
`data/raw/`. Esses dados podem ser baixados no site a seguir: https://synthea.mitre.org/

## Subindo o ambiente completo

O Compose cria dois servidores PostgreSQL isolados:

- `postgres-app`: banco da aplicação, disponível em `localhost:5432`;
- `postgres-airflow`: banco de metadados do Airflow, disponível em `localhost:5433`.
- `streamlit`: painel executivo disponível em `localhost:8501`.

Construa as imagens e suba todos os serviços em segundo plano:

```bash
docker compose up -d --build
```

O serviço `airflow-init` executa automaticamente as migrações e cria o usuário
administrador antes dos demais componentes do Airflow iniciarem.

A interface do Airflow estará disponível em `http://localhost:8080`. Com os valores
padrão do `.env.example`, o usuário e a senha são `airflow`.

O painel executivo estará disponível em `http://localhost:8501`.

Para conferir o estado dos containers:

```bash
docker compose ps
```

Para parar os serviços sem apagar os bancos:

```bash
docker compose down
```

Os volumes dos bancos são preservados. Para acompanhar os logs:

```bash
docker compose logs -f airflow-scheduler
docker compose logs -f streamlit
```

> As credenciais do arquivo de exemplo são apenas para desenvolvimento local.

## Executando a pipeline

### Pelo Airflow

Abra `http://localhost:8080`, acesse a DAG `healthcare_pipeline` e selecione
**Trigger DAG**. O Airflow executará as validações, ingestão e transformações na
ordem configurada.

Quando todas as tarefas estiverem verdes, atualize `http://localhost:8501` para
visualizar os indicadores.

### Pela linha de comando

```bash
poetry run healthcare-analytics
```

Se quiser limpar os schemas antes de recriar todo o pipeline:

```bash
poetry run healthcare-analytics --reset
```

## Executando o reset do banco

```bash
poetry run python -m healthcare_analytics.reset_db
```

Para executar sem exibir a mensagem de aviso:

```bash
poetry run python -m healthcare_analytics.reset_db --no-confirm
```

## Rodando testes

```bash
poetry run task tests
```

O comando exibe no terminal as linhas não cobertas e exige cobertura mínima de 70%.

## Qualidade do código

```bash
poetry run task lint
poetry run task format
```

## Rodando a documentação

```bash
poetry run mkdocs serve
```

A documentação será servida localmente e pode ser acessada em:

```text
http://127.0.0.1:8000
```
