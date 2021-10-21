from data import Data
import unittest


class TestParser(unittest.TestCase):
    def test_exit_number_lines(self):
        expected = "Error! The number of lines, is less than the minimum number of 10 lines"
        file_names = ['./output_test/test_data/TJPI-contracheque.xlsx',
                './output_test/test_data/TJPI-direitos-pessoais.xlsx',
                './output_test/test_data/TJPI-indenizações.xlsx',
                './output_test/test_data/TJPI-direitos-eventuais.xlsx']

        with self.assertRaises(SystemExit) as cm:
            dados = Data(file_names)
            dados.validate
        self.assertEqual(cm.exception.code, expected)
        

if __name__ == '__main__':
    unittest.main()