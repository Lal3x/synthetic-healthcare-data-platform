# Pipeline de Dados

A execução do projeto segue uma sequência lógica e bem organizada para transformar dados brutos em informações analíticas.

## Orquestração no Airflow

A DAG `healthcare_pipeline` é executada manualmente e não possui agendamento
automático. Ela aceita apenas uma execução ativa por vez e segue esta ordem:

```text
verificar_banco ───────┐
                       ├──> criar_schemas -> carregar_bronze
verificar_arquivos ────┘                         ↓
                                      transformar_silver
                                                ↓
                                          agregar_gold
```

Se uma validação inicial falhar, as tarefas dependentes não são executadas. Os
detalhes ficam disponíveis nos logs de cada tarefa na interface do Airflow.

Estados mais comuns na interface:

- verde: tarefa concluída;
- vermelho: tarefa falhou;
- em execução: tarefa ainda está processando;
- `upstream_failed`: uma dependência anterior falhou.

## 1. Coleta e ingestão

Os dados são lidos a partir de arquivos CSV. Essa etapa representa a entrada do sistema e é a base para o restante do fluxo.

## 2. Camada Bronze

Nesta etapa, os dados são carregados da forma mais próxima possível do que foi recebido. As principais ações são:

- leitura dos arquivos;
- normalização de colunas;
- registro de metadados da execução;
- persistência em schemas bronze.

As chaves naturais usadas atualmente são:

- pacientes e atendimentos: `id`;
- condições: `patient`, `encounter`, `code` e `start`.

## 3. Camada Silver

Depois de carregados, os dados passam por validações e transformações. Essa camada é responsável por:

- remover ruídos e dados inconsistentes;
- padronizar nomes e formatos;
- tratar valores nulos e campos críticos;
- preparar os dados para análise.

## 4. Camada Gold

A última etapa transforma os dados em modelos mais próximos do consumo analítico. Aqui são criados:

- resumos por paciente;
- resumos por tipo de encontro;
- visões integradas para consultas e relatórios.

## 5. Observabilidade

Durante o processo, o código registra mensagens de status e validações. Isso facilita a identificação de falhas e a compreensão do que aconteceu em cada etapa.

Os logs ficam disponíveis tanto na interface do Airflow quanto em
`logs/airflow/` no host.

## 6. Reexecução segura

O carregamento Bronze usa chaves naturais para inserir registros novos e atualizar
registros alterados sem duplicar os dados já processados. Assim, a DAG pode ser
executada novamente quando os CSVs forem atualizados.

Quando necessário em desenvolvimento, também é possível reiniciar o processo
apagando os schemas antes da execução:

```bash
poetry run healthcare-analytics --reset
```

Esse mecanismo é útil em ambientes de desenvolvimento e testes, auxiliando a reprodução de cenários e a validação de novas regras de negócio.

## Consumo no Streamlit

O painel em `http://localhost:8501` consulta as tabelas Gold e mantém um cache de
60 segundos. O botão **Atualizar dados** limpa esse cache e recarrega os
indicadores.
