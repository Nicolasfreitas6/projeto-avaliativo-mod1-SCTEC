#Fase 1 do pipeline: Baixar o .zip do Google Drive, extrair os 4 CSVs e carregar o conteúdo (Sem alterações) para o Raw.

#Idempotente: Usa TRUNCATE antes de carregar, entao pode rodar quantas vezes quiser sem duplicar dados.

import zipfile
import gdown
import pandas as pd

from banco import conectar, executar, inserir_em_lote
from config import (
    ARQUIVOS,
    CSV_ENCODING,
    CSV_SEPARADOR,
    DRIVE_FILE_ID,
    PASTA_DADOS,
    TAMANHO_BLOCO
)

NOME_ZIP = "dados_viagens.zip"

#Baixando o .zip do Drive para a pasta data/, se ainda não existir
def baixar_zip():
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    caminho_zip = PASTA_DADOS / NOME_ZIP

    print(f'Baixando .zip do Google Drive (ID: DRIVE_FILE_ID)')
    gdown.download(id=DRIVE_FILE_ID, output=str(caminho_zip), quiet=False)
    return caminho_zip

#Extraindo os CSV's do .zip para a pasta data/.
def extrair_zip(caminho_zip):
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(PASTA_DADOS)
    print(f'Arquivos etraídos em: {PASTA_DADOS}')

#Esvazia a tabela Raw antes de recarregar (idempotencia)
def truncar_tabela(conexao, tabela_raw):
    executar(conexao, f'TRUNCATE TABLE {tabela_raw}')

#Lendo CSV em blocos e inserindo cada bloco na Raw
def carregar_csv_em_blocos(conexao, caminho_csv, tabela_raw, num_colunas):
    placeholders = ", ".join(["%s"] * num_colunas)
    sql_insert = f"INSERT INTO {tabela_raw} VALUES ({placeholders})"
    total_inserido = 0
    leitor = pd.read_csv(
        caminho_csv,
        sep=CSV_SEPARADOR,
        encoding=CSV_ENCODING,
        dtype=str,
        chunksize=TAMANHO_BLOCO,
    )

    for bloco in leitor:
        bloco = bloco.where(pd.notnull(bloco), None)
        linhas = [tuple(linha) for linha in bloco.itertuples(index=False, name=None)]
        inserir_em_lote(conexao, sql_insert, linhas)
        total_inserido += len(linhas)
        print(f"  {tabela_raw}: {total_inserido} linhas inseridas...")
 
    return total_inserido

def main():
    conexao = None
    try:
        caminho_zip = baixar_zip()
        extrair_zip(caminho_zip)
 
        conexao = conectar()
 
        for chave, info in ARQUIVOS.items():
            caminho_csv = PASTA_DADOS / info["csv"]
            tabela_raw = info["tabela_raw"]
 
            print(f"\nProcessando {info['csv']} -> {tabela_raw}")
            truncar_tabela(conexao, tabela_raw)
 
            #Le so o cabecalho pra saber quantas colunas a tabela precisa
            cabecalho = pd.read_csv(
                caminho_csv, sep=CSV_SEPARADOR, encoding=CSV_ENCODING, nrows=0
            )
            num_colunas = len(cabecalho.columns)
 
            total = carregar_csv_em_blocos(conexao, caminho_csv, tabela_raw, num_colunas)
            print(f"  Total: {total} linhas carregadas em {tabela_raw}.")
 
        print("\nExtracao concluida com sucesso.")
 
    except Exception as erro:
        print(f"\nERRO durante a extracao: {erro}")
        raise
 
    finally:
        if conexao:
            conexao.close()
 
if __name__ == "__main__":
    main()