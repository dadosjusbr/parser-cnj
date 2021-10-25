from parser_cnj import parse
import unittest
import json
from google.protobuf.json_format import MessageToDict
from data import load


class TestParser(unittest.TestCase):

    def test_jan_2018(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('./output_test/test_parser/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['output_test/test_parser/TJRJ-contracheque.xlsx',
                 'output_test/test_parser/TJRJ-direitos-eventuais.xlsx',
                 'output_test/test_parser/TJRJ-direitos-pessoais.xlsx',
                 'output_test/test_parser/TJRJ-indenizações.xlsx']
        
        dados = load(files)
        result_data = parse(dados, 'tjrj/01/2018')
        # Converto o resultado do parser, em dict
        result_to_dict = MessageToDict(result_data)
        self.assertEqual(expected, result_to_dict)
        

if __name__ == '__main__':
    unittest.main()
