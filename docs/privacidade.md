# Dados sintéticos e privacidade

## Origem

O projeto utiliza exclusivamente dados gerados pelo
[Synthea](https://synthea.mitre.org/), um gerador de populações clínicas
sintéticas. Nenhum prontuário real é necessário para executar o pipeline.

## Identificadores

Os arquivos do Synthea podem conter nomes, endereços, números de documentos e
identificadores com aparência realista. Esses valores são fictícios, mas devem
ser tratados com cuidado para não causar interpretação incorreta.

Por isso:

- os CSVs não são versionados;
- o notebook é publicado sem outputs;
- exemplos na documentação evitam nomes e documentos;
- o dashboard deve ser apresentado como demonstração;
- dados reais de saúde não devem ser usados neste projeto.

## Limitações

As distribuições do Synthea não representam necessariamente a realidade de uma
população ou sistema de saúde específico. Os indicadores servem para demonstrar
engenharia e visualização de dados, não para orientar decisões clínicas.
