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


if __name__ == '__main__':
    unittest.main()
