import data
import unittest


class TestData(unittest.TestCase):
    def test_validate_existence(self):
        files = [
            "output_test/test_data/contracheque-tjpi-2019-03.xlsx",
            "output_test/test_data/direitos-pessoais-tjpi-2019-03.xlsx",
            "output_test/test_data/indenizacoes-tjpi-2019-03.xlsx",
            "output_test/test_data/direitos-eventuais-tjpi-2019-03.xlsx",
            "output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx",
        ]

        with self.assertRaises(SystemExit) as cm:
            dados = data.load(files, "2019", "09", "TJRR")
            dados.validate()
        self.assertEqual(cm.exception.code, data.STATUS_DATA_UNAVAILABLE)

    def test_validate_zeroless(self):
        files = [
            "output_test/test_data/contracheque-tjpe-2019-05.xlsx",
            "output_test/test_data/direitos-pessoais-tjpe-2019-05.xlsx",
            "output_test/test_data/indenizacoes-tjpe-2019-05.xlsx",
            "output_test/test_data/direitos-eventuais-tjpe-2019-05.xlsx",
            "output_test/test_data/controle-de-arquivos-tjpe-2019-05.xlsx",
        ]
        dados = data.load(files, "2019", "05", "TJPE")
        dados.validate()

    def test_validate_summary(self):
        files = [
            "output_test/test_data/contracheque-tjba-2019-06.xlsx",
            "output_test/test_data/direitos-pessoais-tjba-2019-06.xlsx",
            "output_test/test_data/indenizacoes-tjba-2019-06.xlsx",
            "output_test/test_data/direitos-eventuais-tjba-2019-06.xlsx",
            "output_test/test_data/controle-de-arquivos-tjba-2019-06.xlsx",
        ]
        with self.assertRaises(SystemExit) as cm:
            dados = data.load(files, "2019", "06", "TJBA")
            dados.validate()
        self.assertEqual(cm.exception.code, data.STATUS_DATA_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
