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

    def test_total_zerado_usa_os_valores_da_linha(self):
        # TJDFT 07/2026: a coluna Total das planilhas de categoria vem 0, e o painel repete o valor
        # numa segunda coluna Outra com Detalhe 0 (F9). Juíza aposentada e pensionista com o mesmo nome.
        nome = 'DELEANE CAMARGO DE SANTANA FERNANDES'
        contracheque = [
            ['TJDFT', nome, '07/2026', 'JD0001 JUIZ DE DIREITO', '99000007 APOSENTADOS', 39753.21, 19877.0, 1501.78, 0.0,
             61131.99, 6564.6, 9513.11, 0.0, 3325.72, 19403.43, 41728.56, 0, 0.0],
            ['TJDFT', nome, '07/2026', 'PENSÃO CIVIL', 'PENSÃO CIVIL', 27434.9, 8787.55, 0.0, 0.0,
             36222.45, 0.0, 0.0, 204.93, 5661.25, 5866.18, 30356.27, 0, 0.0],
        ]
        indenizacoes = [['TJDFT', nome, '07/2026', 0, 0, 1501.78, 0, 0, 0, 0, 0, 1501.78, 0, 0, 0, 0]]
        pessoais = [
            ['TJDFT', nome, '07/2026', 0.0, 8787.55, 'VANT PESSOAL - ATS - PA 25971/2022 - INATIVO', 8787.55, 0, 0],
            ['TJDFT', nome, '07/2026', 0.0, 19877.0, 'PARCELA VALORIZACAO TEMPO ANTIGUIDADE CAR PENSAO', 19877.0, 0, 0],
        ]
        folha, _ = parse(dados(contracheque, indenizacoes=indenizacoes, pessoais=pessoais,
                               court='tjdft', month='07'), 'tjdft/07/2026')
        juiza, pensao = folha.contra_cheque
        self.assertEqual(1501.78, itens(juiza)[('indenizações', 'Auxílio Saúde')])
        self.assertNotIn('indenizações', {c for c, _ in itens(pensao)})
        self.assertIn(('direitos-pessoais', 'PARCELA VALORIZACAO TEMPO ANTIGUIDADE CAR PENSAO'), itens(juiza))
        self.assertIn(('direitos-pessoais', 'VANT PESSOAL - ATS - PA 25971/2022 - INATIVO'), itens(pensao))

    def test_linha_dividida_com_nome_repetido(self):
        # Painel novo: uma linha por texto de Detalhe. As partes do mesmo vínculo não podem
        # ser empurradas para o outro vínculo do nome.
        nome = 'FULANA'
        d = dados([cc('TRT2', nome, '07/2026', 'DESEMBARGADOR', 1000.0, dp=3384.97),
                   cc('TRT2', nome, '07/2026', 'PENSIONISTA', 900.0, dp=500.0)],
                  pessoais=[dp('TRT2', nome, '07/2026', 218.39, 'VPNI - MAGISTRADO'),
                            dp('TRT2', nome, '07/2026', 3166.58, 'VPNI - MAGISTRADO - PROVISORIO'),
                            dp('TRT2', nome, '07/2026', 500.0, 'VPNI - PENSAO')],
                  court='trt2', month='07')
        folha, _ = parse(d, 'trt2/07/2026')
        soma = lambda m: round(sum(v for (c, _), v in itens(m).items() if c == 'direitos-pessoais'), 2)
        self.assertEqual([3384.97, 500.0], [soma(m) for m in folha.contra_cheque])

    def test_totais_iguais_nos_dois_vinculos(self):
        # Dois vínculos com o mesmo total na categoria: cada linha vai para um vínculo.
        nome = 'FULANO'
        d = dados([cc('TRT1', nome, '07/2026', 'JUIZ', 1000.0, ind=1000.0),
                   cc('TRT1', nome, '07/2026', 'PENSIONISTA', 900.0, ind=1000.0)],
                  indenizacoes=[ind('TRT1', nome, '07/2026', outra=1000.0, detalhe='A'),
                                ind('TRT1', nome, '07/2026', outra=1000.0, detalhe='B')],
                  month='07')
        folha, _ = parse(d, 'trt1/07/2026')
        self.assertEqual([('indenizações', 'A'), ('indenizações', 'B')],
                         [next(k for k in itens(m) if k[0] == 'indenizações') for m in folha.contra_cheque])

    def test_linha_exata_tem_prioridade(self):
        # TJSC 08/2026: a linha de 944,90 não bate com nenhum vínculo (detalhe diferente do
        # contracheque) e vem antes da linha de 14.095,32, que bate com o primeiro vínculo.
        nome = 'ROGERIO MARIANO DO NASCIMENTO'
        eventuais = lambda valor: ['TJSC', nome, '08/2026', 0, 0, 0, 0, 0, valor, 0, 0, 0, 0, 0, '0', 0, '0', valor]
        d = dados([cc('TJSC', nome, '08/2026', 'JUIZ', 1000.0, de=14095.32),
                   cc('TJSC', nome, '08/2026', 'JUIZ', 1000.0, de=1835.8)],
                  eventuais=[eventuais(944.9), eventuais(14095.32)], court='tjsc', month='08')
        folha, _ = parse(d, 'tjsc/08/2026')
        soma = lambda m: round(sum(r.valor for r in m.remuneracoes.remuneracao if r.categoria == 'direitos-eventuais'), 2)
        self.assertEqual([14095.32, 944.9], [soma(m) for m in folha.contra_cheque])


# Linhas reais dos backups das coletas (contracheque e planilhas de categoria do CNJ).
CRISTINA = 'CRISTINA SOLANGE ROCHA XAVIER'
CRISTINA_2024_10 = [
    ['TRT1', CRISTINA, '10/2024', 'JUIZ TITULAR DE VARA DO TRABALHO', 'INATIVO', 64315.34, 2077.57, 0, 0,
     66392.91, 5358.18, 9209.25, 0, -20943.47, -6376.04, 72768.95, 0, 0],
    ['TRT1', CRISTINA, '10/2024', 'PENSIONISTA', 'PENSIONISTA', 64315.34, 2077.57, 0, 0,
     66392.91, 5358.18, 9209.25, 0, -20943.47, -6376.04, 72768.95, 0, 0],
]


def subsidio(membro):
    return itens(membro).get(('contracheque', 'Subsídio'), 0.0)


class TestRepeticaoIdentica(unittest.TestCase):
    # Até 03/2025 o painel repetia o mesmo pagamento em uma linha por cargo da carreira, com
    # todos os valores iguais, e as planilhas de categoria tinham uma linha só para o nome.
    def setUp(self):
        parser_cnj.sem_detalhamento = False

    def test_repeticao_identica_vira_um_contracheque(self):
        # TRT1 10/2024: mesmo pagamento como juíza titular e como pensionista.
        d = dados(CRISTINA_2024_10,
                  pessoais=[['TRT1', CRISTINA, '10/2024', 0, 2077.57, '-', 0, '0', 2077.57]],
                  court='trt1', month='10', year='2024')
        folha, _ = parse(d, 'trt1/10/2024')
        self.assertEqual(1, len(folha.contra_cheque))
        membro = folha.contra_cheque[0]
        # Cargo e lotação da última linha, como no banco hoje.
        self.assertEqual(('PENSIONISTA', 'PENSIONISTA'), (membro.funcao, membro.local_trabalho))
        self.assertEqual('trt1/10/2024/1', membro.id_contra_cheque)
        self.assertEqual(64315.34, subsidio(membro))
        self.assertEqual(2077.57, itens(membro)[('direitos-pessoais', '-')])

    def test_repeticao_e_vinculo_distinto(self):
        # Repetição idêntica e um vínculo com outros valores: dois contracheques, e as posições
        # seguem sem buraco para o próximo nome.
        outra = ['TRT1', CRISTINA, '10/2024', 'PENSIONISTA', 'PENSIONISTA', 19876.61] + [0] * 12
        d = dados(CRISTINA_2024_10 + [outra, cc('TRT1', 'FULANO', '10/2024', 'JUIZ', 1000.0)],
                  court='trt1', month='10', year='2024')
        folha, _ = parse(d, 'trt1/10/2024')
        self.assertEqual([64315.34, 19876.61, 1000.0], [subsidio(m) for m in folha.contra_cheque])
        self.assertEqual(['trt1/10/2024/1', 'trt1/10/2024/2', 'trt1/10/2024/3'],
                         [m.id_contra_cheque for m in folha.contra_cheque])

    def test_valor_diferente_em_uma_coluna_e_outro_vinculo(self):
        # Basta uma coluna de valor diferente (aqui, Diárias) para serem dois vínculos.
        linhas = [list(r) for r in CRISTINA_2024_10]
        linhas[1][17] = 100.0
        folha, _ = parse(dados(linhas, court='trt1', month='10', year='2024'), 'trt1/10/2024')
        self.assertEqual(2, len(folha.contra_cheque))


class TestPadroesTRT(unittest.TestCase):
    # Os quatro padrões de nome repetido com valores diferentes nos TRTs (2025 e 2026).
    # Cada linha do contracheque continua sendo um contracheque.
    def setUp(self):
        parser_cnj.sem_detalhamento = False

    def confere(self, contracheque, chave, esperado, **planilhas):
        org, mes, ano = chave.split('/')
        folha, _ = parse(dados(contracheque, court=org, month=mes, year=ano, **planilhas), chave)
        self.assertEqual(esperado, [(m.funcao, m.local_trabalho, subsidio(m)) for m in folha.contra_cheque])
        return folha

    def test_magistrado_que_recebe_pensao(self):
        # TRT11 10/2025, painel antigo: as planilhas de categoria somam os dois vínculos numa
        # linha só, que fica no primeiro vínculo (decisão D1).
        nome = 'RILDO CORDEIRO RODRIGUES'
        lot = 'GABINETE DO JUIZ TITULAR DA 15A VT DE MANAUS'
        folha = self.confere(
            [['TRT11', nome, '10/2025', 'JUIZ TITULAR DE VARA', lot, 39753.21, 12128.39, 63883.41, 13251.07,
              129016.08, 7136.16, 10445.77, 0, 15694.85, 33276.78, 95739.3, 0, 0],
             ['TRT11', nome, '10/2025', 'PENSIONISTA', 'PENSIONISTA', 14953.32, 0, 16199.43, 0,
              31152.75, 0, 672.03, 0, 0, 672.03, 30480.72, 0, 0]],
            'trt11/10/2025',
            [('JUIZ TITULAR DE VARA', lot, 39753.21), ('PENSIONISTA', 'PENSIONISTA', 14953.32)],
            indenizacoes=[['TRT11', nome, '10/2025', 1784.42, 0, 1092, 0, 0, 0, 0, '0', 0, '0', 77206.42, '-', 80082.84]])
        soma = lambda m: round(sum(v for (c, _), v in itens(m).items() if c == 'indenizações'), 2)
        self.assertEqual(80082.84, round(sum(soma(m) for m in folha.contra_cheque), 2))

    def test_mudanca_de_cargo_no_mes(self):
        # TRT1 10/2026, painel novo: uma linha por vínculo também nas planilhas de categoria.
        nome = 'ANDRE GUSTAVO BITTENCOURT VILLELA'
        lot = 'GAB DES. ANDRE GUSTAVO BITTENCOURT VILLELA'
        vpni = 'VPNI (ADICIONAL POR TEMPO DE SERVIÇO) - MAGISTRADO'
        folha = self.confere(
            [['TRT1', nome, '10/2026', 'DESEMBARGADOR DO TRABALHO', lot, 41845.49, 7264.89, 29291.84, 329.36,
              78731.58, 988.07, 12153.05, 0, 1756.12, 14897.24, 63834.34, 0, 0],
             ['TRT1', nome, '10/2026', 'JUIZ TITULAR DE VARA DO TRABALHO', lot, 0, 0, 0, 755.96,
              755.96, 0, 0, 0, 0, 0, 755.96, 0, 0]],
            'trt1/10/2026',
            [('DESEMBARGADOR DO TRABALHO', lot, 41845.49), ('JUIZ TITULAR DE VARA DO TRABALHO', lot, 0.0)],
            pessoais=[['TRT1', nome, '10/2026', 988.07, 6276.82, vpni, 0, '0', 7264.89],
                      ['TRT1', nome, '10/2026', 0, 0, '0', 0, '0', 0]])
        desembargador, juiz = folha.contra_cheque
        self.assertEqual(6276.82, itens(desembargador)[('direitos-pessoais', vpni)])
        self.assertNotIn('direitos-pessoais', {c for c, _ in itens(juiz)})

    def test_pagamento_avulso_em_linha_separada(self):
        # TRT1 05/2026: aposentado com uma linha extra sem lotação ('0'), só com um estorno.
        # A linha extra vira um contracheque próprio (decisão D2), com os descontos dela.
        nome = 'ANGELO GALVAO ZAMORANO'
        folha = self.confere(
            [['TRT1', nome, '05/2026', 'DESEMBARGADOR DO TRABALHO', '0', 0, 0, 0, -31675.13,
              -31675.13, -1999.21, 2567.86, 0, 0, 568.65, -32243.78, 0, 0],
             ['TRT1', nome, '05/2026', 'DESEMBARGADOR DO TRABALHO', 'INATIVO', 0, 0, 14645.92, 0,
              14645.92, 7641.47, 0, 0, 0, 7641.47, 7004.45, 0, 0]],
            'trt1/05/2026',
            [('DESEMBARGADOR DO TRABALHO', '0', 0.0), ('DESEMBARGADOR DO TRABALHO', 'INATIVO', 0.0)])
        avulso, inativo = folha.contra_cheque
        self.assertEqual(-2567.86, itens(avulso)[('contracheque', 'Imposto de renda')])
        self.assertEqual(-7641.47, itens(inativo)[('contracheque', 'Previdência Pública')])

    def test_ativo_e_aposentado_no_mesmo_mes(self):
        # TRT15 06/2026: mesmo cargo, uma linha como INATIVO e outra com a lotação da vara.
        nome = 'MARCELO BUENO PALLONE'
        vara = 'VARA DO TRABALHO DE CAMPO LIMPO PAULISTA'
        self.confere(
            [['TRT15', nome, '06/2026', 'JUIZ TITULAR DE VARA', 'INATIVO', 34266.67, 1195.03, 10031.5, 18343.61,
              63836.81, 0, 3135.85, 0, 0, 3135.85, 60700.96, 0, 0],
             ['TRT15', nome, '06/2026', 'JUIZ TITULAR DE VARA', vara, 0, 0, 0, 274934.05,
              274934.05, 988.07, 4460.39, 0, 0, 5448.46, 269485.59, 0, 0]],
            'trt15/06/2026',
            [('JUIZ TITULAR DE VARA', 'INATIVO', 34266.67), ('JUIZ TITULAR DE VARA', vara, 0.0)])


if __name__ == '__main__':
    unittest.main()
