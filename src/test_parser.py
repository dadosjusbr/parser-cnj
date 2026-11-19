import json
import unittest
import shutil
import tempfile

from google.protobuf.json_format import MessageToDict

from data import load
from headers_keys import INDENIZACOES
from parser_cnj import parse, cria_remuneracao


class TestParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_jan_2018(self):
        self.maxDiff = None
        # Json com a saida esperada
        with open('src/output_test/test_parser/expected.json', 'r') as fp:
            expected = json.load(fp)

        files = ['src/output_test/test_parser/contracheque-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/direitos-eventuais-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/direitos-pessoais-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/indenizacoes-tjrj-2018-01.xlsx',
                 'src/output_test/test_parser/controle-de-arquivos-tjrj-2018-01.xlsx']

        dados = load(files, '2018', '01', 'TJRJ', self.test_dir)
        result_data = parse(dados, 'tjrj/01/2018')
        # Converto o resultado do parser, em dict
        result_to_dict = MessageToDict(result_data[0], float_precision=2)
        self.assertEqual(expected, result_to_dict)

    def test_spreadsheet_with_one_line(self):
        # Em caso de dados sumarizados, haverá um erro de SystemExit(4)
        with self.assertRaises(SystemExit) as err:
            self.maxDiff = None

            files = ['src/output_test/test_parser/test_one_line/contracheque-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/direitos-eventuais-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/direitos-pessoais-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/indenizacoes-tjpi-2020-01.xlsx',
                     'src/output_test/test_parser/test_one_line/controle-de-arquivos-tjpi-2020-01.xlsx']

            dados = load(files, '2020', '01', 'TJPI', self.test_dir)
            result_data = parse(dados, 'tjpi/01/2020')

        exc = err.exception
        self.assertEqual(exc.code, 4)

    def test_detalhe_com_numeros(self):
        # A planilha de direitos eventuais tem um campo detalhe com um número.
        # Este pode ser interpretado como int, o que dá erro, pois deveria ser unicode.
        files = ['src/output_test/test_parser/test_one_line/contracheque-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/direitos-eventuais-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/direitos-pessoais-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/indenizacoes-tjma-2020-01.xlsx',
                 'src/output_test/test_parser/test_one_line/controle-de-arquivos-tjma-2020-01.xlsx']

        dados = load(files, '2020', '01', 'TJMA', self.test_dir)
        folha = parse(dados, 'tjma/01/2020')

        # Só checar que não deu erro.
        self.assertEqual(1, len(folha[0].contra_cheque))

    def test_detalhe_com_quebra_de_linha(self):
        # O painel exporta o CR do campo "Detalhe" como '_x000D_'; o item deve trazer o CR original.
        row = ['TJGO', 'MAGISTRADO', '09/2026', 0, 0, 0, 0, 0, 0,
               20911.27, '- PVTAC,_x000D_GECJAO', 0, 0, 0, 0, 20911.27]
        remuneracoes, _ = cria_remuneracao(row, INDENIZACOES)

        itens = [r.item for r in remuneracoes.remuneracao]
        self.assertIn('- PVTAC,\rGECJAO', itens)
        self.assertFalse(any('_x000D_' in item for item in itens))

    def test_magistrado_com_dois_vinculos(self):
        # TJGO 09/2026: o mesmo nome aparece como desembargadora e como pensionista.
        # Cada linha do contracheque deve virar um contracheque, e as outras planilhas
        # devem ir para o vínculo cujo total da categoria bate com o da linha.
        nome = 'AVELIRDES ALMEIDA PINHEIRO DE LEMOS'
        contracheque = [
            ['TJGO', nome, '09/2026', 'DESEMBARGADOR', '0', 41845.49, 14645.92, 27199.54, 0.0,
             83690.95, 6179.68, 9618.97, 0, 10125.22, 25923.87, 57767.08, 0, 0],
            ['TJGO', nome, '09/2026', 'PENSIONISTA DE MAGISTRADO', '0', 37586.56, 0.0, 1879.33, 0.0,
             39465.89, 4928.58, 7548.62, 0, 0.0, 12477.2, 26988.69, 0, 0],
        ]
        indenizacoes = [
            ['TJGO', nome, '09/2026', 0.0, 0.0, 0.0, 0, 0, 0, 1879.33, '- PVTAC', 0.0, '-', 0, '-', 1879.33],
            ['TJGO', nome, '09/2026', 0.0, 0.0, 6276.79, 0, 0, 0, 14645.92, '- PVTAC', 6276.83, '- DIF. PVTAC', 0, '-', 27199.54],
        ]
        direitos_pessoais = [
            ['TJGO', nome, '09/2026', 0.0, 14645.92, '- VPNI', 0, '-', 14645.92],
            ['TJGO', nome, '09/2026', 0.0, 0.0, '-', 0, '-', 0.0],
        ]
        dados = type('Dados', (), dict(contracheque=contracheque, indenizacoes=indenizacoes,
                                       direitos_eventuais=[], direitos_pessoais=direitos_pessoais,
                                       court='TJGO', month='09', year='2026'))
        folha, _ = parse(dados, 'tjgo/09/2026')

        self.assertEqual(2, len(folha.contra_cheque))
        desembargadora, pensionista = folha.contra_cheque
        self.assertEqual('DESEMBARGADOR', desembargadora.funcao)
        self.assertEqual('PENSIONISTA DE MAGISTRADO', pensionista.funcao)
        itens = lambda m: {(r.categoria, r.item): r.valor for r in m.remuneracoes.remuneracao if r.valor}
        self.assertEqual(41845.49, itens(desembargadora)[('contracheque', 'Subsídio')])
        self.assertEqual(6276.83, itens(desembargadora)[('indenizações', '- DIF. PVTAC')])
        self.assertEqual(14645.92, itens(desembargadora)[('direitos-pessoais', '- VPNI')])
        self.assertEqual(1879.33, itens(pensionista)[('indenizações', '- PVTAC')])
        self.assertNotIn(('direitos-pessoais', '- VPNI'), itens(pensionista))


if __name__ == '__main__':
    unittest.main()
