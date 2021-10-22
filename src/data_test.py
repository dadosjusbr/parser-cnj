from data import Data
import unittest


class TestData(unittest.TestCase):
    def test_validate(self):
        file_names = ['./output_test/test_data/TJPI-contracheque.xlsx',
                './output_test/test_data/TJPI-direitos-pessoais.xlsx',
                './output_test/test_data/TJPI-indenizações.xlsx',
                './output_test/test_data/TJPI-direitos-eventuais.xlsx']

        with self.assertRaises(SystemExit) as cm:
            dados = Data(file_names)
            dados.validate()
        self.assertEqual(cm.exception.code, 1)
        

if __name__ == '__main__':
    unittest.main()