# Testes dos casos encontrados na revisão de 11/2026, com linhas tiradas dos dados reais.
import math
import unittest

import data
import number
import parser_cnj
from parser_cnj import parse

CC_VAZIO = [0.0] * 13


def cc(trib, nome, ref, cargo, subsidio, dp=0.0, ind=0.0, de=0.0):
    # 18 colunas: Tribunal, Magistrado, Mês/Ano, Cargo, Lotação, Subsídio, DP, Ind, DE, ...
    return [trib, nome, ref, cargo, 'LOTACAO', subsidio, dp, ind, de] + [0.0] * 9


def ind(trib, nome, ref, alimentacao=0.0, outra=0.0, detalhe='0', total=None):
    total = alimentacao + outra if total is None else total
    return [trib, nome, ref, alimentacao, 0, 0, 0, 0, 0, outra, detalhe, 0, '0', 0, '0', total]


def dp(trib, nome, ref, outra=0.0, detalhe='0', total=None):
    total = outra if total is None else total
    return [trib, nome, ref, 0.0, outra, detalhe, 0, '0', total]


def dados(contracheque, indenizacoes=(), eventuais=(), pessoais=(), court='TRT1', month='03', year='2026'):
    return type('Dados', (), dict(contracheque=list(contracheque), indenizacoes=list(indenizacoes),
                                  direitos_eventuais=list(eventuais), direitos_pessoais=list(pessoais),
                                  court=court, month=month, year=year))


def itens(membro):
    return {(r.categoria, r.item): round(r.valor, 2) for r in membro.remuneracoes.remuneracao if r.valor}


class TestRevisao(unittest.TestCase):
    def setUp(self):
        parser_cnj.sem_detalhamento = False

    def test_planilha_de_categoria_vazia(self):
        d = dados([cc('TRT1', 'FULANO', '03/2026', 'JUIZ', 1000.0)])
        folha, sem_detalhamento = parse(d, 'trt1/03/2026')
        self.assertEqual(1, len(folha.contra_cheque))
        self.assertFalse(sem_detalhamento)

    def test_planilha_ausente(self):
        with self.assertRaises(SystemExit) as cm:
            data._arquivo(['/output/contracheque-trerj-2026-09.xlsx'], 'indenizacoes')
        self.assertEqual(data.STATUS_DATA_UNAVAILABLE, cm.exception.code)

    def test_sem_linhas_do_orgao_nao_vira_coleta_vazia(self):
        d = dados([cc('TRT1', 'FULANO', '02/2026', 'JUIZ', 1000.0)])
        with self.assertRaises(SystemExit) as cm:
            parse(d, 'trt1/03/2026')
        self.assertEqual(data.STATUS_INVALID_FILE, cm.exception.code)

    def test_numeros_em_texto(self):
        # Painel antigo, trt15 07/2026: Antecipação de férias '-24035' era gravada como 0.
        self.assertEqual(-24035.0, number.format_element('-24035'))
        self.assertEqual(-1234.56, number.format_element('-1234,56'))
        self.assertEqual(1234.56, number.format_element('1.234,56'))
        self.assertEqual(3045.99, number.format_element('3,045.99'))
        self.assertEqual(99999.99, number.format_element('99999,99'))
        self.assertEqual(0.0, number.format_element('R$  -'))
        self.assertEqual(0.0, number.format_element('-'))
        self.assertEqual(0.0, number.format_element(math.nan))
        self.assertEqual(12145.18, number.format_element(12145.18))

    def test_valor_em_texto_invalido_sai_com_5(self):
        # Texto com dígito que não vira número não pode ser gravado como 0.
        nome = 'FULANO'
        d = dados([cc('TRT1', nome, '03/2026', 'JUIZ', 1000.0, ind=12.3)],
                  indenizacoes=[ind('TRT1', nome, '03/2026', alimentacao='12a,3', total=12.3)])
        with self.assertRaises(SystemExit) as cm:
            parse(d, 'trt1/03/2026')
        self.assertEqual(data.STATUS_INVALID_FILE, cm.exception.code)

    def test_homonimo_de_tribunal_vizinho_nao_entra(self):
        # F7, trt1 03/2026: o arquivo do coletor antigo trazia TRT1 e TRT10 juntos.
        nome = 'ADRIANA MEIRELES MELONIO'
        d = dados([cc('TRT1', nome, '03/2026', 'JUIZ', 1000.0),
                   cc('TRT10', nome, '03/2026', 'JUIZ', 37765.55, ind=1860.51)],
                  indenizacoes=[ind('TRT10', nome, '03/2026', alimentacao=1860.51)],
                  court='trt1')
        folha, _ = parse(d, 'trt1/03/2026')
        self.assertEqual(1, len(folha.contra_cheque))
        self.assertNotIn(('indenizações', 'Auxílio-alimentação'), itens(folha.contra_cheque[0]))

    def test_tribunal_com_espaco_e_minusculo(self):
        d = dados([cc(' trt1 ', 'FULANO', '03/2026', 'JUIZ', 1000.0)], court='TRT1')
        folha, _ = parse(d, 'trt1/03/2026')
        self.assertEqual(1, len(folha.contra_cheque))

    def test_cabecalho_fora_de_ordem(self):
        colunas = ['Tribunal', 'Magistrado', 'Mês/Ano Ref.', 'Abono de permanência (R$)', 'Detalhe',
                   'Outra (R$)', 'Outra (R$).1', 'Detalhe.1', 'Total de Direitos Pessoais']
        with self.assertRaises(SystemExit) as cm:
            data._confere_cabecalho(colunas, 'direitos-pessoais', 'x.xlsx')
        self.assertEqual(data.STATUS_INVALID_FILE, cm.exception.code)
        data._confere_cabecalho(['Tribunal', 'Magistrado', 'Mês/Ano Ref.', 'Abono de permanência (R$)', 'Outra (R$)',
                                 'Detalhe', 'Outra (R$).1', 'Detalhe.1', 'Total de Direitos Pessoais'],
                                'direitos-pessoais', 'x.xlsx')

    def test_um_magistrado_detalhado_nao_e_sumarizado(self):
        controle = [['TRT1', '03/2026', 'TRT1_03_26.xls 01/04/2026', 1, 1, 1, 1]]
        d = data.Data([cc('TRT1', 'FULANO', '03/2026', 'JUIZ', 1000.0)], [], [], [], controle, '2026', '03', 'trt1')
        d.validate()

    def test_linha_sumarizada_do_orgao(self):
        controle = [['TRT1', '03/2026', 'TRT1_03_26.xls 01/04/2026', 1, 1, 1, 1]]
        d = data.Data([cc('TRT1', '0', '03/2026', '0', 1000.0)], [], [], [], controle, '2026', '03', 'trt1')
        with self.assertRaises(SystemExit) as cm:
            d.validate()
        self.assertEqual(data.STATUS_DATA_UNAVAILABLE, cm.exception.code)

    def test_par_invertido_da_o_mesmo_resultado(self):
        # F1/F3, trt1 07/2026: juiz titular e pensionista com o mesmo nome, em ordens diferentes
        # nos dois painéis. Cada vínculo deve ficar com o seu subsídio e as suas verbas.
        nome = 'MAUREN XAVIER SEELING'
        titular = cc('TRT1', nome, '07/2026', 'JUIZ TITULAR', 39753.21, ind=1000.0)
        pensao = cc('TRT1', nome, '07/2026', 'PENSIONISTA', 48122.04, ind=500.0)
        linhas_ind = [ind('TRT1', nome, '07/2026', outra=500.0, detalhe='PVTAC'),
                      ind('TRT1', nome, '07/2026', outra=1000.0, detalhe='PVTAC')]
        resultados = []
        for ordem in ([titular, pensao], [pensao, titular]):
            folha, _ = parse(dados(ordem, indenizacoes=linhas_ind, month='07'), 'trt1/07/2026')
            resultados.append(sorted((m.funcao, itens(m)[('contracheque', 'Subsídio')],
                                      itens(m)[('indenizações', 'PVTAC')]) for m in folha.contra_cheque))
        self.assertEqual(resultados[0], resultados[1])
        self.assertIn(('JUIZ TITULAR', 39753.21, 1000.0), resultados[0])

    def test_detalhe_dividido_em_varias_linhas(self):
        # Painel novo, trt2 07/2026: o painel antigo juntava a VPNI de ANA MARIA BRISOLA numa
        # linha com Detalhe '-' (3.384,97); o novo traz uma linha por texto de Detalhe.
        nome = 'ANA MARIA BRISOLA'
        d = dados([cc('TRT2', nome, '07/2026', 'DESEMBARGADOR', 41845.49, dp=3384.97)],
                  pessoais=[dp('TRT2', nome, '07/2026', 218.39, 'VPNI (ADICIONAL POR TEMPO DE SERVIÇO) - MAGISTRADO'),
                            dp('TRT2', nome, '07/2026', 3166.58, 'VPNI (ADICIONAL POR TEMPO DE SERVIÇO) - MAGISTRADO - PROVISÓRIO')],
                  court='trt2', month='07')
        folha, _ = parse(d, 'trt2/07/2026')
        soma = sum(v for (c, _), v in itens(folha.contra_cheque[0]).items() if c == 'direitos-pessoais')
        self.assertAlmostEqual(3384.97, soma, places=2)


if __name__ == '__main__':
    unittest.main()
