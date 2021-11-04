from data import load
import unittest

file_names = ['./output_test/test_data/contracheque-tjpi-2019-03.xlsx',
                './output_test/test_data/direitos-pessoais-tjpi-2019-03.xlsx',
                './output_test/test_data/indenizacoes-tjpi-2019-03.xlsx',
                './output_test/test_data/direitos-eventuais-tjpi-2019-03.xlsx',
                './output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx']

class TestData(unittest.TestCase):
        
    def test_validate_existence(self):
        STATUS_DATA_UNAVAILABLE = 4
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, '2019', '09')
            dados.validate()
        self.assertEqual(cm.exception.code, STATUS_DATA_UNAVAILABLE)

if __name__ == '__main__':
    unittest.main()