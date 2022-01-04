"""O codigo do crawler é escrito na liguagem GO.
Pode ser visto aqui: https://github.com/dadosjusbr/coletor-cnj
"""
import sys
import os
import subprocess

import pandas as pd

# Se for erro de não existir planilhas o retorno vai ser esse:
STATUS_DATA_UNAVAILABLE = 4
# Caso o erro for a planilha, que é invalida por algum motivo, o retorno vai ser esse:
STATUS_INVALID_FILE = 5


def _read(file):
    try:
        data = pd.read_excel(file, engine="openpyxl").to_numpy()
    except Exception as excep:
        print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
        sys.exit(STATUS_INVALID_FILE)
    return data


def _convert_file(file, output_path):
    """
    Converte os arquivos ODS que estão corrompidos, para XLSX.
    """
    subprocess.run(
        ["libreoffice", "--headless", "--invisible", "--convert-to", "xlsx", file], capture_output=True, text=True
    )  # Pega a saída para não interferir no print dos dados
    file_name = file.split(sep="/")[-1]
    file_name = f'{file_name.split(sep=".")[0]}.xlsx'
    # Move para o diretório passado por parâmetro
    subprocess.run(["mv", file_name, f"{output_path}/{file_name}"])
    return f"{output_path}/{file_name}"


def load(file_names, year, month, court, output_path):
    """Carrega os arquivos passados como parâmetros.

    :param file_names: slice contendo os arquivos baixados pelo coletor.
    Os nomes dos arquivos devem seguir uma convenção e começar com contracheque,
    indenizações, direitos-eventuais e direitos_pessoais.

    :param year e month: usados para fazer a validação na planilha de controle de dados

    :return um objeto Data() pronto para operar com os arquivos
    """

    contracheque = _read(_convert_file(
        [c for c in file_names if "contracheque" in c][0], output_path))
    indenizacoes = _read(_convert_file(
        [i for i in file_names if "indenizacoes" in i][0], output_path))
    direitos_eventuais = _read(
        _convert_file(
            [de for de in file_names if "direitos-eventuais" in de][0], output_path)
    )
    direitos_pessoais = _read(
        _convert_file(
            [dp for dp in file_names if "direitos-pessoais" in dp][0], output_path)
    )
    controle_de_arquivos = _read(
        _convert_file(
            [ca for ca in file_names if "controle-de-arquivos" in ca][0], output_path)
    )

    return Data(
        contracheque,
        indenizacoes,
        direitos_eventuais,
        direitos_pessoais,
        controle_de_arquivos,
        year,
        month,
        court,
    )


class Data:
    def __init__(
        self,
        contracheque,
        indenizacoes,
        direitos_eventuais,
        direitos_pessoais,
        controle_de_arquivos,
        year,
        month,
        court,
    ):
        self.contracheque = contracheque
        self.indenizacoes = indenizacoes
        self.direitos_eventuais = direitos_eventuais
        self.direitos_pessoais = direitos_pessoais
        self.controle_de_arquivos = controle_de_arquivos
        self.year = year
        self.month = month
        self.court = court

    def validate(self):
        """Validação inicial dos arquivos passados como parâmetros.
        Aborta a execução do script em caso de erro.

        Caso o validade fique pare o script na leitura da planilha 
        de controle de dados dara um erro retornando o codigo de erro 4,
        esse codigo significa que não existe dados para a data pedida.
        """
        # Esses nome vem do conteúdo do arquivo controle-de-arquivos.
        # Ex: TJPI_01_21.xls
        month_zeroless = self.month.lstrip("0")
        FILE_NAME = f"{self.court}_{self.month}_{self.year[2:]}.xls".lower()
        FILE_NAME_ZEROLESS = f"{self.court}_{month_zeroless}_{self.year[2:]}.xls".lower(
        )
        have_spreadsheet = False

        for row in self.controle_de_arquivos:
            # As vezes os arquivos vem com a extensão em maiúsculo.
            lrow = str(row).lower()
            if FILE_NAME in lrow or FILE_NAME_ZEROLESS in lrow:
                have_spreadsheet = True
                break

        if not have_spreadsheet:
            sys.stderr.write(
                f"Não existem planilhas contendo o string {FILE_NAME} na entrada {self.controle_de_arquivos}.")
            sys.exit(STATUS_DATA_UNAVAILABLE)

        # Estamos dando erro quando não temos dados detalhados. Isto pois todo o pipeline
        # de processamento do CNJ assume detalhe.
        # Discussão em: https://github.com/dadosjusbr/parser-cnj/issues/32
        if len(self.contracheque) == 1:
            sys.stderr.write(f"Dados de contracheque sumarizados.")
            sys.exit(STATUS_DATA_UNAVAILABLE)
