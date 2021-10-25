from data import load
import unittest

file_names = ['./output_test/test_data/TJPI-contracheque.xlsx',
                './output_test/test_data/TJPI-direitos-pessoais.xlsx',
                './output_test/test_data/TJPI-indenizações.xlsx',
                './output_test/test_data/TJPI-direitos-eventuais.xlsx',
                './output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx']

class TestData(unittest.TestCase):
    def test_validate_rows(self):
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, '2021', '09')
            dados.validate()
        self.assertEqual(cm.exception.code, 5)
        
    def test_validate_existence(self):
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, '2019', '09')
            dados.validate()
        self.assertEqual(cm.exception.code, 4)

if __name__ == '__main__':
    unittest.main()