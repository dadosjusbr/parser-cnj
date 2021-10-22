import pandas as pd
import sys
import os


class Data:
    def __init__(self, file_names):
        for file in file_names:
            if 'contracheque' in file:
                self.contracheque = self.__read(file)
            if 'indenizações' in file:
                self.indenizacoes = self.__read(file)
            if 'direitos-eventuais' in file:
                self.direitos_eventuais = self.__read(file)
            if 'direitos-pessoais' in file:
                self.direitos_pessoais = self.__read(file)

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