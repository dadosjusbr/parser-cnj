import data
import unittest
import shutil
import tempfile


class TestData(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_validate_existence(self):
        files = [
            "src/output_test/test_data/contracheque-tjpi-2019-03.xlsx",
            "src/output_test/test_data/direitos-pessoais-tjpi-2019-03.xlsx",
            "src/output_test/test_data/indenizacoes-tjpi-2019-03.xlsx",
            "src/output_test/test_data/direitos-eventuais-tjpi-2019-03.xlsx",
            "src/output_test/test_data/controle-de-arquivos-tjrr-2019-09.xlsx",
        ]

        with self.assertRaises(SystemExit) as cm:
            dados = data.load(files, "2019", "09", "TJRR", self.test_dir)
            dados.validate()
        self.assertEqual(cm.exception.code, data.STATUS_DATA_UNAVAILABLE)

    def test_not_zip(self):
        files = [
            "src/output_test/test_data/contracheque-tjrr-2018-01.xlsx",
            "src/output_test/test_data/direitos-pessoais-tjrr-2018-01.xlsx",
            "src/output_test/test_data/indenizacoes-tjrr-2018-01.xlsx",
            "src/output_test/test_data/direitos-eventuais-tjrr-2018-01.xlsx",
            "src/output_test/test_data/controle-de-arquivos-tjrr-2018-01.xlsx",
        ]

        dados = data.load(files, "2018", "01", "TJRR", self.test_dir)
        dados.validate()

    def test_validate_zeroless(self):
        files = [
            "src/output_test/test_data/contracheque-tjpe-2019-05.xlsx",
            "src/output_test/test_data/direitos-pessoais-tjpe-2019-05.xlsx",
            "src/output_test/test_data/indenizacoes-tjpe-2019-05.xlsx",
            "src/output_test/test_data/direitos-eventuais-tjpe-2019-05.xlsx",
            "src/output_test/test_data/controle-de-arquivos-tjpe-2019-05.xlsx",
        ]
        dados = data.load(files, "2019", "05", "TJPE", self.test_dir)
        dados.validate()

    def test_validate_summary(self):
        files = [
            "src/output_test/test_data/contracheque-tjba-2019-06.xlsx",
            "src/output_test/test_data/direitos-pessoais-tjba-2019-06.xlsx",
            "src/output_test/test_data/indenizacoes-tjba-2019-06.xlsx",
            "src/output_test/test_data/direitos-eventuais-tjba-2019-06.xlsx",
            "src/output_test/test_data/controle-de-arquivos-tjba-2019-06.xlsx",
        ]
        with self.assertRaises(SystemExit) as cm:
            dados = data.load(files, "2019", "06", "TJBA", self.test_dir)
            dados.validate()
        self.assertEqual(cm.exception.code, data.STATUS_DATA_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
