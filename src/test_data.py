from data import load
import unittest

file_names = [
    "output_test/test_data/contracheque-tjpi-2019-03.xlsx",
    "output_test/test_data/direitos-pessoais-tjpi-2019-03.xlsx",
    "output_test/test_data/indenizacoes-tjpi-2019-03.xlsx",
    "output_test/test_data/direitos-eventuais-tjpi-2019-03.xlsx",
    "output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx",
]

file_names_zeroless = [
    "output_test/test_data/contracheque-tjpe-2019-05.xlsx",
    "output_test/test_data/direitos-pessoais-tjpe-2019-05.xlsx",
    "output_test/test_data/indenizacoes-tjpe-2019-05.xlsx",
    "output_test/test_data/direitos-eventuais-tjpe-2019-05.xlsx",
    "output_test/test_data/controle-de-arquivos-tjpe-2019-05.xlsx",
]


class TestData(unittest.TestCase):
    def test_validate_existence(self):
        STATUS_DATA_UNAVAILABLE = 4
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, "2019", "09", "TJRR")
            dados.validate()
        self.assertEqual(cm.exception.code, STATUS_DATA_UNAVAILABLE)

    def test_validate_zeroless(self):
        dados = load(file_names_zeroless, "2019", "05", "TJPE")
        dados.validate()


if __name__ == "__main__":
    unittest.main()
