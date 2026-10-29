import json
import unittest
import shutil
import tempfile

from google.protobuf.json_format import MessageToDict

from data import load
from headers_keys import INDENIZACOES
from parser_cnj import parse, cria_remuneracao


class TestParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_jan_2018(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('src/output_test/test_parser/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['src/output_test/test_parser/contracheque-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/direitos-eventuais-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/direitos-pessoais-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/indenizacoes-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/controle-de-arquivos-tjrj-2018-01.xlsx']

        dados = load(files, '2018', '01', 'TJRJ', self.test_dir)
        result_data = parse(dados, 'tjrj/01/2018')
        # Converto o resultado do parser, em dict
        result_to_dict = MessageToDict(result_data[0], float_precision=2)
        self.assertEqual(expected, result_to_dict)

    def test_spreadsheet_with_one_line(self):
        # Em caso de dados sumarizados, haverá um erro de SystemExit(4)
        with self.assertRaises(SystemExit) as err:
            self.maxDiff = None

            files = ['src/output_test/test_parser/test_one_line/contracheque-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/direitos-eventuais-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/direitos-pessoais-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/indenizacoes-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/controle-de-arquivos-tjpi-2020-01.xlsx']

            dados = load(files, '2020', '01', 'TJPI', self.test_dir)
            result_data = parse(dados, 'tjpi/01/2020')

        exc = err.exception
        self.assertEqual(exc.code, 4)

    def test_detalhe_com_numeros(self):
        # A planilha de direitos eventuais tem um campo detalhe com um número.
        # Este pode ser interpretado como int, o que dá erro, pois deveria ser unicode.
        files = ['src/output_test/test_parser/test_one_line/contracheque-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/direitos-eventuais-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/direitos-pessoais-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/indenizacoes-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/controle-de-arquivos-tjma-2020-01.xlsx']

        dados = load(files, '2020', '01', 'TJMA', self.test_dir)
        folha = parse(dados, 'tjma/01/2020')

        # Só checar que não deu erro.
        self.assertEqual(1, len(folha[0].contra_cheque))

    def test_detalhe_com_quebra_de_linha(self):
        # O painel exporta o CR do campo "Detalhe" como '_x000D_'; o item deve trazer o CR original.
        row = ['TJGO', 'MAGISTRADO', '09/2026', 0, 0, 0, 0, 0, 0,
               20911.27, '- PVTAC,_x000D_GECJAO', 0, 0, 0, 0, 20911.27]
        remuneracoes, _ = cria_remuneracao(row, INDENIZACOES)

        itens = [r.item for r in remuneracoes.remuneracao]
        self.assertIn('- PVTAC,\rGECJAO', itens)
        self.assertFalse(any('_x000D_' in item for item in itens))


if __name__ == '__main__':
    unittest.main()
