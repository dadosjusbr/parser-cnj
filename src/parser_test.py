from unittest.case import expectedFailure
from parser_cnj import parse
import unittest
from google.protobuf import text_format
import json
from google.protobuf.json_format import MessageToJson, MessageToDict


class TestParser(unittest.TestCase):

    def test_jan_2018(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('./output_test/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['./output_test/TJRJ-contracheque.xlsx',
                 './output_test/TJRJ-direitos-eventuais.xlsx',
                 './output_test/TJRJ-direitos-pessoais.xlsx',
                 './output_test/TJRJ-indenizações.xlsx']

        folha = parse(files, 'tjrj/01/2018')
        # Converto o resultado do parser, em dict
        json_obj = MessageToDict(folha)
        self.assertEqual(expected, json_obj)
        

if __name__ == '__main__':
    unittest.main()
