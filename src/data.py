"""O codigo do crawler é escrito na liguagem GO.
Pode ser visto aqui: https://github.com/dadosjusbr/coletor-cnj
"""
import sys
import os
import subprocess
import unicodedata

import pandas as pd

# Se for erro de não existir planilhas o retorno vai ser esse:
STATUS_DATA_UNAVAILABLE = 4
# Caso o erro for a planilha, que é invalida por algum motivo, o retorno vai ser esse:
STATUS_INVALID_FILE = 5


# O parser lê as colunas pela posição (headers_keys.HEADERS). Se o painel mudar a ordem
# ou o número de colunas, os valores iriam para os itens errados sem nenhum erro.
CABECALHOS = {
    "contracheque": ["tribunal", "magistrado", "mes/ano", "cargo", "lotacao", "subsidio",
                     "direitos pessoais", "indenizacoes", "direitos eventuais", "total de rendimentos",
                     "previdencia", "imposto de renda", "descontos diversos", "retencao por teto",
                     "total de descontos", "rendimento liquido", "remuneracao do orgao de origem", "diarias"],
    "indenizacoes": ["tribunal", "magistrado", "mes/ano", "auxilio-alimentacao", "auxilio pre-escolar",
                     "auxilio saude", "auxilio natalidade", "auxilio moradia", "ajuda de custo",
                     "outra", "detalhe", "outra", "detalhe", "outra", "detalhe", "total"],
    "direitos-eventuais": ["tribunal", "magistrado", "mes/ano", "abono constitucional", "indenizacao de ferias",
                           "antecipacao de ferias", "gratificacao natalina", "antecipacao de gratificacao natalina",
                           "substituicao", "gratificacao por exercicio cumulativo", "gratificacao por encargo",
                           "pagamentos retroativos", "jeton", "outra", "detalhe", "outra", "detalhe", "total"],
    "direitos-pessoais": ["tribunal", "magistrado", "mes/ano", "abono de permanencia",
                          "outra", "detalhe", "outra", "detalhe", "total"],
}


def _normaliza(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().lower()


def _confere_cabecalho(colunas, tipo, file):
    """Encerra com 'arquivo inválido' se as colunas não forem as esperadas, na mesma ordem."""
    esperado = CABECALHOS.get(tipo)
    if esperado is None:
        return
    colunas = [_normaliza(c) for c in colunas]
    if len(colunas) != len(esperado) or any(not c.startswith(e) for c, e in zip(colunas, esperado)):
        sys.stderr.write(f"Cabeçalho inesperado em {file}: {list(colunas)}")
        sys.exit(STATUS_INVALID_FILE)


def _read(file, tipo=None):
    try:
        df = pd.read_excel(file, engine="openpyxl")
    except Exception as excep:
        print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
        sys.exit(STATUS_INVALID_FILE)
    _confere_cabecalho(df.columns, tipo, file)
    return df.to_numpy()


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


def _arquivo(file_names, tipo):
    """Retorna o arquivo do tipo pedido ou encerra com 'dados indisponíveis' se o coletor não o baixou."""
    arquivos = [f for f in file_names if tipo in f]
    if not arquivos:
        sys.stderr.write(f"Planilha de {tipo} não encontrada entre os arquivos do coletor.")
        sys.exit(STATUS_DATA_UNAVAILABLE)
    return arquivos[0]


def load(file_names, year, month, court, output_path):
    """Carrega os arquivos passados como parâmetros.

    :param file_names: slice contendo os arquivos baixados pelo coletor.
    Os nomes dos arquivos devem seguir uma convenção e começar com contracheque,
    indenizações, direitos-eventuais e direitos_pessoais.

    :param year e month: usados para fazer a validação na planilha de controle de dados

    :return um objeto Data() pronto para operar com os arquivos
    """

    contracheque = _read(_convert_file(_arquivo(file_names, "contracheque"), output_path), "contracheque")
    indenizacoes = _read(_convert_file(_arquivo(file_names, "indenizacoes"), output_path), "indenizacoes")
    direitos_eventuais = _read(_convert_file(_arquivo(file_names, "direitos-eventuais"), output_path), "direitos-eventuais")
    direitos_pessoais = _read(_convert_file(_arquivo(file_names, "direitos-pessoais"), output_path), "direitos-pessoais")
    controle_de_arquivos = _read(_convert_file(_arquivo(file_names, "controle-de-arquivos"), output_path))

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
        # A coluna Magistrado possui valor '0' quando os dados estão sumarizados, não consideramos os dados se esse for o caso.
        # Discussão em: https://github.com/dadosjusbr/parser-cnj/issues/32
        # Olha só as linhas do próprio órgão: no arquivo misturado do coletor antigo, a
        # primeira linha podia ser de outro tribunal, e um órgão com um só magistrado
        # (uma linha) não está necessariamente sumarizado.
        linhas = [r for r in self.contracheque
                  if isinstance(r[0], str) and r[0].strip().casefold() == self.court.strip().casefold()]
        if not linhas:
            sys.stderr.write(f"Nenhuma linha de {self.court} no contracheque.")
            sys.exit(STATUS_INVALID_FILE)
        if any(r[1] in (0, '0') for r in linhas):
            sys.stderr.write(f"Dados de contracheque sumarizados.")
            sys.exit(STATUS_DATA_UNAVAILABLE)
