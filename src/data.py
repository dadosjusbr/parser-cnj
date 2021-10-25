import pandas as pd
import sys
import os


    def __read(file):
        try:
            data = pd.read_excel(file, engine='openpyxl').to_numpy()
        except Exception as excep:
            print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
            sys.exit(1)

        return data
        
def load(file_names)
    """Carrega os arquivos passados como parâmetros.
    
    :param file_names: slice contendo os arquivos baixados pelo coletor. Os nomes dos arquivos devem seguir uma convenção e começar com contracheque, indenizações, direitos-eventuais e direitos_pessoais.
    :return um objeto Data() pronto para operar com os arquivos
    """
    d = Data()
    for file in file_names:
        if 'contracheque' in file:
            data.contracheque = __read(file)
        if 'indenizações' in file:
            data.indenizacoes = __read(file)
        if 'direitos-eventuais' in file:
            data.direitos_eventuais = __read(file)
        if 'direitos-pessoais' in file:
            data.direitos_pessoais = __read(file)
    return data
 
class Data:
    def __init__(self, contracheque, indenizacoes, direitos_eventuais, direitos_pessoais):
        self.contracheque = contracheque
        self.indenizacoes = indenizacoes
        self.direitos_eventuais = direitos_eventuais
        self.direitos_pessoais = direitos_pessoais

    def validate(self):
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

    def __read(self, file):
        try:
            data = pd.read_excel(file, engine='openpyxl').to_numpy()
        except Exception as excep:
            print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
            sys.exit(1)

        return data
