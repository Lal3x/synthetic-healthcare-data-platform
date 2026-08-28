# Testes e Cobertura

Os testes unitários validam leitura de arquivos, transformações Silver,
agregações Gold, configuração, conexão simulada, criação e reset de schemas e a
ordem de execução do pipeline. Eles usam mocks nas integrações e não exigem que os
containers ou o PostgreSQL estejam ativos.

## Executar a suíte

```bash
poetry run task tests
```

O comando executa o pytest uma única vez e mostra as linhas não cobertas no
terminal:

```bash
pytest tests -v --cov=healthcare_analytics --cov-report=term-missing --cov-fail-under=70
```

## Cobertura atual

Na última validação local, a suíte apresentou:

- 39 testes aprovados;
- 77% de cobertura total;
- 100% em leitores Bronze, configurações e agregações Gold;
- 96% nas regras de transformação Silver;
- 88% na orquestração principal;
- 94% na criação de schemas;
- 88% na conexão com o banco;
- 85% no reset do ambiente.

A principal oportunidade de evolução está na ingestão idempotente Bronze, que
possui mais interações específicas com PostgreSQL. Esse cenário pode ser coberto
futuramente com testes de integração usando um banco temporário.

O projeto exige no mínimo 70% de cobertura. O comando retorna erro e interrompe o
CI quando o resultado fica abaixo dessa meta.

O relatório é exibido somente no terminal. O projeto não gera `coverage.xml`,
pois atualmente não utiliza Codecov, SonarCloud ou outro consumidor desse formato.

## Integração contínua

O workflow `.github/workflows/ci.yml` usa Python 3.13, instala as dependências,
executa pre-commit, formatação, lint e a suíte com cobertura.

Após a aprovação do job de qualidade, o job Docker do mesmo `ci.yml` valida o
Compose e constrói as imagens do Airflow e do Streamlit. A dependência entre os
jobs impede o build das imagens quando os testes ou verificações anteriores falham.

## Dependências e segurança

O Dependabot verifica semanalmente atualizações para GitHub Actions, dependências
Python e imagens Docker. SAST com CodeQL não está habilitado porque o repositório
privado atual não possui GitHub Code Security. SAST e DAST permanecem como
evoluções futuras.
