import pandas as pd
import sys
import os


def _read(file):
        try:
            data = pd.read_excel(file, engine='openpyxl').to_numpy()
        except Exception as excep:
            print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
            sys.exit(1)

        return data
        
def load(file_names, year, month):
    """Carrega os arquivos passados como parâmetros.
    
    :param file_names: slice contendo os arquivos baixados pelo coletor. Os nomes dos arquivos devem seguir uma convenção e começar com contracheque, indenizações, direitos-eventuais e direitos_pessoais.
    :return um objeto Data() pronto para operar com os arquivos
    """
    
    contracheque = _read([c for c in file_names if 'contracheque' in c][0])
    indenizacoes = _read([i for i in file_names if 'indenizações' in i][0])
    direitos_eventuais = _read([de for de in file_names if 'direitos-eventuais' in de][0])
    direitos_pessoais = _read([dp for dp in file_names if 'direitos-pessoais' in dp][0])
    controle_de_arquivos = _read([ca for ca in file_names if 'controle-de-arquivos' in ca][0])
    
    data = Data(contracheque, indenizacoes, direitos_eventuais, direitos_pessoais,
                controle_de_arquivos, year, month)
    return data
 
class Data:
    def __init__(self, contracheque, indenizacoes, direitos_eventuais, direitos_pessoais, 
                controle_de_arquivos, year, month):
        self.year = year
        self.month = month
        self.contracheque = contracheque
        self.indenizacoes = indenizacoes
        self.direitos_eventuais = direitos_eventuais
        self.direitos_pessoais = direitos_pessoais
        self.controle_de_arquivos = controle_de_arquivos

    def validate(self):
        """
        Validação inicial dos arquivos passados como parâmetros. Aborta a execução do script em caso de erro.
        """
        MIN_ROWS = 10

        if len(self.contracheque) < MIN_ROWS or \
                len(self.indenizacoes) < MIN_ROWS or \
                len(self.direitos_eventuais) < MIN_ROWS or \
                len(self.direitos_pessoais) < MIN_ROWS:

            print(
                f"Os arquivos a serem consolidados tem menos que {MIN_ROWS} linhas e, por isso, são considerados inválidos.",
                file=sys.stderr
                )
            sys.exit(1)

    def validate_existence(self):
        have_spreadsheet = False
        for row in self.controle_de_arquivos:
            if f'{self.month}/{self.year}' in row:
                have_spreadsheet = True
        if not have_spreadsheet:
            sys.stderr.write(f'Não existe planilhas para {self.month}/{self.year}')
            sys.exit(1)
