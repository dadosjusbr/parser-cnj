# coding: utf8
import sys
import os
from parser_cnj import parse
from coleta import coleta_pb2 as Coleta, IDColeta
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import text_format
import metadado
import data
import requests

if "COURT" in os.environ:
    court = os.environ["COURT"]
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'COURT'.\n")
    os._exit(1)

if "YEAR" in os.environ:
    year = os.environ["YEAR"]
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'YEAR'.\n")
    os._exit(1)

if "MONTH" in os.environ:
    month = os.environ["MONTH"]
    month = month.zfill(2)
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'MONTH'.\n")
    os._exit(1)

if "GIT_COMMIT" in os.environ:
    PARSER_VERSION = os.environ["GIT_COMMIT"]
else:
    PARSER_VERSION = "unspecified"

# Pegando o ID do último commit do coletor
headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
}
response = requests.get(
    'https://api.github.com/repos/dadosjusbr/coletor-cnj/commits', headers=headers)

if response.status_code == 200:
    response = response.json()
    CRAWLER_VERSION = response[0]["sha"]
else:
    CRAWLER_VERSION = "unspecified"


if "OUTPUT_FOLDER" in os.environ:
    output_path = os.environ["OUTPUT_FOLDER"]
else:
    output_path = "/output"


def parse_execution(data, file_names):
    coleta = Coleta.Coleta()
    coleta.chave_coleta = IDColeta(court, month, year)
    coleta.orgao = court.lower()
    coleta.mes = int(month)
    coleta.ano = int(year)
    coleta.repositorio_coletor = "https://github.com/dadosjusbr/coletor-cnj"
    coleta.versao_coletor = CRAWLER_VERSION
    coleta.repositorio_parser = "https://github.com/dadosjusbr/parser-cnj"
    coleta.versao_parser = PARSER_VERSION
    coleta.arquivos.extend(file_names)
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    coleta.timestamp_coleta.CopyFrom(timestamp)

    # Consolida folha de pagamento
    folha = Coleta.FolhaDePagamento()
    folha = parse(data, coleta.chave_coleta)

    # Monta resultado da coleta.
    rc = Coleta.ResultadoColeta()
    rc.folha.CopyFrom(folha)
    rc.coleta.CopyFrom(coleta)

    metadados = metadado.captura()
    rc.metadados.CopyFrom(metadados)

    # Imprime a versão textual na saída padrão.
    print(text_format.MessageToString(rc), flush=True, end="")


# Main execution
def main():
    file_names = [f.rstrip() for f in sys.stdin.readlines()]

    dados = data.load(file_names, year, month, court, output_path)
    dados.validate()  # Se não acontecer nada, é porque está tudo ok!

    parse_execution(dados, file_names)


if __name__ == "__main__":
    main()
