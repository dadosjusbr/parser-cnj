from data import load
import unittest

file_names = ['./output_test/test_data/TJPI-contracheque.xlsx',
                './output_test/test_data/TJPI-direitos-pessoais.xlsx',
                './output_test/test_data/TJPI-indenizações.xlsx',
                './output_test/test_data/TJPI-direitos-eventuais.xlsx',
                './output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx']

class TestData(unittest.TestCase):
    def test_validate_rows(self):
        STATUS_INVALID_FILE = 5
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, '2021', '09')
            dados.validate()
        self.assertEqual(cm.exception.code, STATUS_INVALID_FILE)
        
    def test_validate_existence(self):
        STATUS_DATA_UNAVAILABLE = 4
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, '2019', '09')
            dados.validate()
        self.assertEqual(cm.exception.code, STATUS_DATA_UNAVAILABLE)

if __name__ == '__main__':
    unittest.main()