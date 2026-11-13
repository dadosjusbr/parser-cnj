CONTRACHEQUE = "contracheque"
INDENIZACOES = "indenizações"
DIREITOS_EVENTUAIS = "direitos-eventuais"
DIREITOS_PESSOAIS = "direitos-pessoais"

# Coluna do contracheque com o total de cada categoria (usada para achar o vínculo
# certo quando o mesmo magistrado aparece em mais de uma linha).
TOTAL_NO_CONTRACHEQUE = {
    DIREITOS_PESSOAIS: 6,
    INDENIZACOES: 7,
    DIREITOS_EVENTUAIS: 8,
}

# Coluna com o total da linha em cada planilha de categoria.
TOTAL_DA_CATEGORIA = {
    INDENIZACOES: 15,
    DIREITOS_EVENTUAIS: 17,
    DIREITOS_PESSOAIS: 8,
}

# Colunas de valor de cada planilha de categoria: as colunas simples e os pares (Outra, Detalhe).
# Usadas para calcular o total da linha quando a coluna Total vem zerada (TJDFT, TJMA, TJSC, TJSE).
VALORES_DA_CATEGORIA = {
    INDENIZACOES: ([3, 4, 5, 6, 7, 8], [(9, 10), (11, 12), (13, 14)]),
    DIREITOS_EVENTUAIS: (list(range(3, 13)), [(13, 14), (15, 16)]),
    DIREITOS_PESSOAIS: ([3], [(4, 5), (6, 7)]),
}

HEADERS = {
    CONTRACHEQUE: {
        "Subsídio": 5,
        "Previdência Pública": 10,
        "Imposto de renda": 11,
        "Descontos Diversos": 12,
        "Retenção por Teto Constitucional": 13,
        "Remuneração do órgão de origem ": 16,
        "Diárias": 17,
    },
    INDENIZACOES: {
        "Auxílio-alimentação": 3,
        "Auxílio Pré-escolar": 4,
        "Auxílio Saúde": 5,
        "Auxílio Natalidade": 6,
        "Auxílio Moradia": 7,
        "Ajuda de Custo": 8,
        "Outra 1": 9,
        "Detalhe 1": 10,
        "Outra 2": 11,
        "Detalhe 2": 12,
        "Outra 3": 13,
        "Detalhe 3": 14,
    },
    DIREITOS_EVENTUAIS: {
        "Abono constitucional de 1/3 de férias": 3,
        "Indenização de férias": 4,
        "Antecipação de férias": 5,
        "Gratificação natalina": 6,
        "Antecipação de gratificação natalina": 7,
        "Substituição": 8,
        "Gratificação por exercício cumulativo": 9,
        "Gratificação por encargo Curso/Concurso": 10,
        "Pagamentos retroativos": 11,
        "JETON": 12,
        "Outra 1": 13,
        "Detalhe 1": 14,
        "Outra 2": 15,
        "Detalhe 2": 16,
    },
}