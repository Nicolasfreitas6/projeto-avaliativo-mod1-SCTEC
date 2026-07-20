# Pipeline de Dados - Viagens a Serviço do Governo Federal

## Descrição do Projeto
Este projeto resolve o problema de desorganização de dados brutos sobre gastos públicos com viagens a serviço disponibilizados pelo Portal da Transparência. A solução constrói um pipeline de dados automatizado de ponta a ponta que extrai, limpa, estrutura e analisa essas informações para apoiar a tomada de decisões transparentes.

O projeto adota a **Arquitetura Medallion**:
* **Camada Raw**: Cópia fiel dos dados brutos em formato texto para fins de auditoria.
* **Camada Silver**: Dados limpos, com tipagem correta e integridade de chaves declarada no banco.
* **Camada Gold**: Tabelas agregadas e visões geradas por SQL para responder a perguntas de negócio.

## Tecnologias Utilizadas
* **Linguagem**: Python 3
* **Banco de Dados**: PostgreSQL
* **Bibliotecas principais**: Pandas, Psycopg2, Matplotlib e Seaborn
* **Versionamento**: Git e GitHub

## Como Executar o Sistema
1. Instale as dependências executando: `pip install -r requirements.txt`.
2. Configure suas credenciais criando um arquivo `.env` baseado no arquivo `.env.example`.
3. Execute o script SQL no PostgreSQL para estruturar o banco: `0_criar_banco.sql`.
4. Execute o script de ingestão: `python 1_extrair.py`.
5. Execute o script de tratamento: `python 2_transformar.py`.
6. Abra e execute o arquivo `3_analise.ipynb` para visualizar as tabelas e gráficos gerados.

## Insights e Conclusões da Análise
A partir das consultas executadas na camada Silver e na Camada Gold Agregada, obtivemos os seguintes insights sobre os gastos de viagens em 2025[cite: 1, 7]:

* **Tipos de Gastos**: As **Diárias** representam o maior valor médio pago por viagem (R$ 2.078,28), seguidas de perto pelas **Passagens** (R$ 1.878,34).
* **Modais de Transporte**: O **Veículo Oficial** é o meio de transporte mais utilizado no total de trechos (386.424 ocorrências), seguido pelo modal **Aéreo** (232.666 ocorrências).
* **Destinos mais Frequentes**: O estado de **São Paulo** foi o destino líder em trechos com 82.722 ocorrências, seguido pelo **Distrito Federal** com 79.962.
* **Concentração de Custos**: O **Ministério da Justiça e Segurança Pública** disparou como o órgão de maior custo total declarado (R$ 7,54 bilhões) e também foi o órgão que mais efetuou pagamentos no total (R$ 488,83 milhões).
* **Viagens de Alto Custo**: Viagens internacionais ou para locais específicos apresentam custos médios altíssimos, tendo como destino principal de maior custo médio a cidade de **Guiyang/China** (R$ 112.870,41 por viagem).
* **Duração Atípica**: A viagem de maior duração registrada foi para o destino de **Mogi Mirim/SP**, com **383 dias** de duração e custo total zerado (R$ 0.0), o que pode indicar um ponto de atenção para auditoria ou dado atípico na base de origem.

## Melhorias Futuras
*Conectar a camada Gold a um painel interativo no Power BI ou Looker Studio.

