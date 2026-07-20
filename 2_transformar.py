#Fase 2 do pipeline: Ler a camada Raw, limpá-la e tipar os dados (String -> Decimal,; String -> Date), calcular colunas derivadas e carregar a camada Silver.

#Idempotente: Usa TRUNCATE e CASCADE antes de carregar.

import pandas as pd
from banco import conectar, executar, inserir_em_lote

#1. Funções de conversão

##Função para converter uma coluna de texto para número real monetário (float) e corrigir incosistências.
def serie_valor_brl(serie):
    limpo = (
        serie.astype(str)
        .str.strip()
        .str.replace('.', '', regex=False) #Remove o separador de milhar dos números
        .str.replace(',', '.', regex=False) #Troca a vírgula de decimal para ponto
    )

    return pd.to_numeric(limpo, errors='coerce')

##Função para converter coluna de texto para datetime
def serie_data_brl(serie):
    return pd.to_datetime(serie.astype(str).str.strip(), format='%d/%m/%Y', errors='coerce')

##Função para converter a coluna datetime para date() do Python ou None
def para_date_ou_none(serie_datetime):
    return serie_datetime.apply(lambda x: x.date() if pd.notna(x) else None)

##Função para inserir um DF inteiro na tabela indicada, tratando NaN/NaT como Null
def inserir_dataframe(conexao, df, tabela, colunas):
    if df.empty:
        print(f'Nenhuma linha inserida em {tabela}.')
        return 0

    df_final = df[colunas].astype(object).where(pd.notnull(df[colunas]), None)
    linhas = [tuple(linha) for linha in df_final.itertuples(index=False, name=None)]
 
    placeholders = ", ".join(["%s"] * len(colunas))
    sql_insert = f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({placeholders})"
    inserir_em_lote(conexao, sql_insert, linhas)
 
    print(f"{tabela}: {len(linhas)} linhas inseridas.")
    return len(linhas)

#2. Transformando cada tabela de Raw para Silver

##Transformando a tabela de viagem
def transformar_viagem(conexao):
    df = pd.read_sql("SELECT * FROM raw_viagem;", conexao)

    #Transformação de colunas monetárias
    for col in ["valor_diarias", "valor_passagens", "valor_devolucao", "valor_outros_gastos"]:
        df[col] = serie_valor_brl(df[col])

    #Transformação de colunas de datas
    df["data_inicio"] = para_date_ou_none(serie_data_brl(df["data_inicio"]))
    df["data_fim"] = para_date_ou_none(serie_data_brl(df["data_fim"]))

    df["valor_total"] = df[["valor_diarias", "valor_passagens", "valor_devolucao", "valor_outros_gastos"]].sum(axis=1, skipna=True)

    #Aqui assumi que a duração = data_fim - Data_inicio (sem +1)
    df["duracao_dias"] = df.apply(
        lambda linha: (linha["data_fim"] - linha["data_inicio"]).days
        if linha["data_fim"] and linha["data_inicio"]
        else None,
        axis=1,
    )
 
    df = df.rename(
        columns={
            "identificador_processo_viagem": "id_viagem",
            "num_proposta_pcdp": "num_proposta",
            "codigo_orgao_superior": "cod_orgao_superior",
        }
    )
 
    colunas = [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente", "cod_orgao_superior",
        "nome_orgao_superior", "nome_viajante", "cargo", "data_inicio", "data_fim",
        "destinos", "motivo", "valor_diarias", "valor_passagens", "valor_devolucao",
        "valor_outros_gastos", "valor_total", "duracao_dias",
    ]
   #Respeita as constraints: PK nao pode ser nula/duplicada; nome_orgao_superior e NOT NULL
    df = df.dropna(subset=["id_viagem"]).drop_duplicates(subset=["id_viagem"])
    df = df[df["nome_orgao_superior"].notna() & (df["nome_orgao_superior"].str.strip() != "")]
 
    inserir_dataframe(conexao, df, "silver_viagem", colunas)
 
    #Devolve o conjunto de ids validos, para os filhos filtrarem contra ele
    return set(df["id_viagem"])
 
##Transformando a tabela de pagamento
def transformar_pagamento(conexao, ids_validos):
    df = pd.read_sql("SELECT * FROM raw_pagamento;", conexao)
 
    df["valor"] = serie_valor_brl(df["valor"])
 
    df = df.rename(
        columns={
            "identificador_processo_viagem": "id_viagem",
            "num_proposta_pcdp": "num_proposta",
            "nome_unidade_gestora_pagadora": "nome_ug_pagadora",
        }
    )
 
    colunas = [
        "id_viagem", "num_proposta", "nome_orgao_pagador", "nome_ug_pagadora",
        "tipo_pagamento", "valor",
    ]
 
    # integridade referencial: descarta linhas cujo id_viagem nao existe na Silver
    df = df[df["id_viagem"].isin(ids_validos)]
    # NOT NULL em tipo_pagamento
    df = df[df["tipo_pagamento"].notna() & (df["tipo_pagamento"].str.strip() != "")]
 
    inserir_dataframe(conexao, df, "silver_pagamento", colunas)
 
##Transformando a tabela de passagem
def transformar_passagem(conexao, ids_validos):
    df = pd.read_sql("SELECT * FROM raw_passagem;", conexao)
 
    for col in ["valor_passagem", "taxa_servico"]:
        df[col] = serie_valor_brl(df[col])
 
    df["data_emissao"] = para_date_ou_none(serie_data_brl(df["data_emissao_compra"]))
 
    df = df.rename(columns={"identificador_processo_viagem": "id_viagem"})
 
    colunas = [
        "id_viagem", "meio_transporte", "pais_origem_ida", "uf_origem_ida",
        "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida", "cidade_destino_ida",
        "valor_passagem", "taxa_servico", "data_emissao",
    ]
 
    df = df[df["id_viagem"].isin(ids_validos)]
 
    inserir_dataframe(conexao, df, "silver_passagem", colunas)
 
##Transformando a tabela de trecho
def transformar_trecho(conexao, ids_validos):
    df = pd.read_sql("SELECT * FROM raw_trecho;", conexao)
 
    df["sequencia_trecho"] = pd.to_numeric(df["sequencia_trecho"], errors="coerce")
    df["numero_diarias"] = serie_valor_brl(df["numero_diarias"])
    df["origem_data"] = para_date_ou_none(serie_data_brl(df["origem_data"]))
    df["destino_data"] = para_date_ou_none(serie_data_brl(df["destino_data"]))
 
    df = df.rename(columns={
        "identificador_processo_viagem": "id_viagem",
        "destino_cidad": "destino_cidade",
    })
 
    colunas = [
        "id_viagem", "sequencia_trecho", "origem_data", "origem_uf", "origem_cidade",
        "destino_data", "destino_uf", "destino_cidade", "meio_transporte", "numero_diarias",
    ]
 
    df = df[df["id_viagem"].isin(ids_validos)]
    # UNIQUE (id_viagem, sequencia_trecho): remove duplicatas exatas, se houver
    df = df.drop_duplicates(subset=["id_viagem", "sequencia_trecho"])
 
    inserir_dataframe(conexao, df, "silver_trecho", colunas)
 
#Orquestracao
def truncar_silver(conexao):
    """Esvazia as 4 tabelas Silver de uma vez (CASCADE cuida da ordem das FKs)."""
    executar(
        conexao,
        """
        TRUNCATE TABLE silver_viagem, silver_pagamento, silver_passagem, silver_trecho
        RESTART IDENTITY CASCADE;
        """,
    )
 
def main():
    conexao = None
    try:
        conexao = conectar()
 
        print("Limpando camada Silver (TRUNCATE)...")
        truncar_silver(conexao)
 
        print("\nTransformando viagem...")
        ids_validos = transformar_viagem(conexao)
 
        print("\nTransformando pagamento...")
        transformar_pagamento(conexao, ids_validos)
 
        print("\nTransformando passagem...")
        transformar_passagem(conexao, ids_validos)
 
        print("\nTransformando trecho...")
        transformar_trecho(conexao, ids_validos)
 
        print("\nTransformacao concluida com sucesso.")
 
    except Exception as erro:
        print(f"\nERRO durante a transformacao: {erro}")
        raise
 
    finally:
        if conexao:
            conexao.close()
 
if __name__ == "__main__":
    main()