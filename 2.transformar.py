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
    df = pd.read_sql('SELECT * FROM raw_viagem;', conexao)

    #Transformação de colunas monetárias
    for col in ['valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos']:
        df[col] = serie_valor_brl(df[col])

    #Transformação de colunas de datas


##Transformando a tabela de pagamento

##Transformando a tabela de passagem

##Transformando a tabela de trecho