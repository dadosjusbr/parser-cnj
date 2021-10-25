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
        
def load(file_names):
    """Carrega os arquivos passados como parâmetros.
    
    :param file_names: slice contendo os arquivos baixados pelo coletor. Os nomes dos arquivos devem seguir uma convenção e começar com contracheque, indenizações, direitos-eventuais e direitos_pessoais.
    :return um objeto Data() pronto para operar com os arquivos
    """
    
    contracheque = _read([c for c in file_names if 'contracheque' in c][0])
    indenizacoes = _read([i for i in file_names if 'indenizações' in i][0])
    direitos_eventuais = _read([de for de in file_names if 'direitos-eventuais' in de][0])
    direitos_pessoais = _read([dp for dp in file_names if 'direitos-pessoais' in dp][0])
    
    data = Data(contracheque, indenizacoes, direitos_eventuais, direitos_pessoais)
    return data
 
class Data:
    def __init__(self, contracheque, indenizacoes, direitos_eventuais, direitos_pessoais):
        self.contracheque = contracheque
        self.indenizacoes = indenizacoes
        self.direitos_eventuais = direitos_eventuais
        self.direitos_pessoais = direitos_pessoais

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

