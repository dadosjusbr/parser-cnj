import json
import unittest

from google.protobuf.json_format import MessageToDict

from data import load
from parser_cnj import parse


class TestParser(unittest.TestCase):
    def test_jan_2018(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('./output_test/test_parser/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['output_test/test_parser/contracheque-tjrj-2018-01.xlsx',
                 'output_test/test_parser/direitos-eventuais-tjrj-2018-01.xlsx',
                 'output_test/test_parser/direitos-pessoais-tjrj-2018-01.xlsx',
                 'output_test/test_parser/indenizacoes-tjrj-2018-01.xlsx',
                 'output_test/test_parser/controle-de-arquivos-tjrj-2018-01.xlsx']
                 
        dados = load(files, '2018', '01', 'TJRJ')
        result_data = parse(dados, 'tjrj/01/2018')
        # Converto o resultado do parser, em dict
        result_to_dict = MessageToDict(result_data)

        self.assertEqual(expected, result_to_dict)


    def test_spreadsheet_with_one_line(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('./output_test/test_parser/test_one_line/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['output_test/test_parser/test_one_line/contracheque-tjpi-2020-01.xlsx',
                'output_test/test_parser/test_one_line/direitos-eventuais-tjpi-2020-01.xlsx',
                'output_test/test_parser/test_one_line/direitos-pessoais-tjpi-2020-01.xlsx',
                'output_test/test_parser/test_one_line/indenizacoes-tjpi-2020-01.xlsx',
                'output_test/test_parser/test_one_line/controle-de-arquivos-tjpi-2020-01.xlsx']

        dados = load(files, '2020', '01', 'TJPI')
        result_data = parse(dados, 'tjpi/01/2020')
        # Converto o resultado do parser, em dict
        result_to_dict = MessageToDict(result_data)

        self.assertEqual(expected, result_to_dict)


if __name__ == '__main__':
    unittest.main()
