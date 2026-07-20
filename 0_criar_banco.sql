--Fase 0 do pipeline de dados do projeto: Criação do banco de dados e das 8 tabelas
--(4 raw + 4 silver), seugindo a Arquitetura Medallion que o próprio projeto propôs.

--Como rodar no pgAdmin:
--1. Conecte na Query Tool do banco "postgres" (o padrão) e rode primeiramente só o bloco:
--CREATE DATABASE transparencia; -> Precisa rodar fora de uma transação e fora do banco que está sendo criado.
--2. Depois de criado o database, abra uma Query Tool dentro do novo banco.
--3. (clique nele na árvore à esquerda) e rode o restante ("PARTE 2"), de criação das tabelas dentro do Database.

--Parte 1: Criando o banco (database)
CREATE DATABASE transparencia;

--Parte 2: Criando as tabelas necessárias
--CAMADA RAW: Camada fiel dos CSV's, com todas as colunas em VARCHAR, sem PK/FK/Constraints
DROP TABLE IF EXISTS raw_viagem;
CREATE TABLE raw_viagem(
    identificador_processo_viagem VARCHAR(255),
    num_proposta_pcdp VARCHAR(255),
    situacao VARCHAR (4000),
    viagem_urgente VARCHAR (4000),
    justificativa_urgencia_viagem VARCHAR (4000),
    codigo_orgao_superior VARCHAR(255),
    nome_orgao_superior VARCHAR (255255),
    nome_orgao_superior VARCHAR (255),
    codigo_orgao_solicitante VARCHAR(255),
    nome_orgao_solicitante VARCHAR(4000),
    cpf_viajante VARCHAR(255),
    nome_viajante VARCHAR(4000),
    cargo VARCHAR(4000),
    funcao VARCHAR(4000),
    descricao_funcao VARCHAR(4000),
    data_inicio VARCHAR(255),
    data_fim VARCHAR(255),
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias VARCHAR(255),
    valor_passagens VARCHAR(255),255
    valor_passagens VARCHAR(255),
    valor_devolucao VARCHAR(255),
    valor_outros_gastos VARCHAR(255)
);

DROP TABLE IF EXISTS raw_pagamento;
CREATE TABLE raw_pagamento (
    identificador_processo_viagem VARCHAR(255),
    num_proposta_pcdp VARCHAR(255),
    codigo_orgao_superior VARCHAR(255),
    nome_orgao_superior VARCHAR(4000),
    codigo_orgao_pagador VARCHAR(255),
    nome_orgao_pagador VARCHAR(4000),
    codigo_unidade_gestora_pagadora VARCHAR(255),
    nome_unidade_gestora_pagadora VARCHAR(4000),
    tipo_pagamento VARCHAR(4000),
    valor VARCHAR(255)255
    valor VARCHAR(255)
);

DROP TABLE IF EXISTS raw_passagem;
CREATE TABLE raw_passagem (
    identificador_processo_viagem VARCHAR(255),
    num_proposta_pcdp VARCHAR(255),
    meio_transporte VARCHAR(4000),
    pais_origem_ida VARCHAR(4000),
    uf_origem_ida VARCHAR(4000),
    cidade_origem_ida VARCHAR(4000),
    pais_destino_ida VARCHAR(4000),
    uf_destino_ida VARCHAR(4000),
    cidade_destino_ida VARCHAR(4000),
    pais_origem_volta VARCHAR(4000),
    uf_origem_volta VARCHAR(4000),255
    cidade_origem_volta VARCHAR(4000),
    pais_destino_volta VARCHAR(4000),
    uf_destino_volta VARCHAR(4000),
    cidade_destino_volta VARCHAR(4000),
    valor_passagem VARCHAR(255),
    taxa_servico VARCHAR(255),
    data_emissao_compra VARCHAR(255),
    hora_emissao_compra VARCHAR(255)
);

DROP TABLE IF EXISTS raw_trecho;
CREATE TABLE raw_trecho (
    identificador_processo_viagem VARCHAR(255),
    255 VARCHAR(255),
    sequencia_trecho VARCHAR(255),
    origem_data VARCHAR(255),
    origem_pais VARCHAR(4000),
    origem_uf VARCHAR(4000),
    origem_cidade VARCHAR(4000),
    destino_data VARCHAR(255),
    destino_pais VARCHAR(4000),
    destino_uf VARCHAR(4000),
    destino_cidad VARCHAR(4000),
    meio_transporte VARCHAR(4000),
    numero_diarias VARCHAR(255),
    missao VARCHAR(255)
);

--CAMADA SILVER: Dados limpos, tipados, com PK, FK e constraints (NOT NULL, CHECK, UNIQUE).
DROP TABLE IF EXISTS silver_viagem;
CREATE TABLE silver_viagem (
    id_viagem VARCHAR(20) PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2) CHECK (valor_diarias >= 0),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2),
    duracao_dias INT
);

DROP TABLE IF EXISTS silver_pagamento;
CREATE TABLE silver_pagamento(
    id_pagamento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem (id_viagem),
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL, 
    valor DECIMAL(10,2) CHECK (valor >= 0)
);

DROP TABLE IF EXISTS silver_passagem;
CREATE TABLE silver_passagem (
    id_passagem INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem (id_viagem),
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2) CHECK (valor_passagem >= 0),
    taxa_servico DECIMAL(10,2) CHECK (taxa_servico >= 0),
    data_emissao DATE
);

DROP TABLE IF EXISTS silver_trecho;
CREATE TABLE silver_trecho (
    id_trecho INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL REFERENCES silver_viagem (id_viagem),
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2) CHECK (numero_diarias >= 0),
    UNIQUE (id_viagem, sequencia_trecho)
);