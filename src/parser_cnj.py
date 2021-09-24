# coding: utf8
import pandas as pd
import sys
import os
from  coleta import coleta_pb2 as Coleta

CONTRACHEQUE = 'contracheque'
INDENIZACOES = 'indenizações'
DIREITOS_EVENTUAIS = 'direitos-eventuais'
DIREITOS_PESSOAIS = '-direitos-pessoais'
MEMBRO = 0
RECEITA = 0
DESPESA = 1
BASE = 0
OUTROS = 1

HEADERS = {
    CONTRACHEQUE: {
        'Subsídio': 3,
        'Previdência Pública': 8,
        'Imposto de renda': 9,
        'Descontos Diversos': 10,
        'Retenção por Teto Constitucional': 11,
        'Remuneração do órgão de origem ': 14,
        'Diárias':15,
    },
    INDENIZACOES: {
        'Auxílio-alimentação': 3,
        'Auxílio Pré-escolar': 4,
        'Auxílio Saúde': 5,
        'Auxílio Natalidade': 6,
        'Auxílio Moradia': 7,
        'Ajuda de Custo': 8,
        'Outra 1': 9,
        'Detalhe 1': 10,
        'Outra 2': 11,
        'Detalhe 2': 12,
        'Outra 3': 13,
        'Detalhe 3': 14,
    },
    DIREITOS_EVENTUAIS:{
        'Abono constitucional de 1/3 de férias': 3,
        'Indenização de férias': 4,
        'Antecipação de férias': 5,
        'Gratificação natalina': 6,
        'Antecipação de gratificação natalina': 7,
        'Substituição': 8,
        'Gratificação por exercício cumulativo': 9,
        'Gratificação por encargo Curso/Concurso': 10,
        'Pagamentos retroativos': 11,
        'JETON': 12,
        'Outra 1': 13,
        'Detalhe 1': 14,
        'Outra 2': 15,
        'Detalhe 2': 16,
    },
    DIREITOS_PESSOAIS : {
        'Abono de permanência':3,
        'Outra 1': 4,
        'Detalhe 1': 5,
        'Outra 2': 6,
        'Detalhe 2': 7,
    },
}

def read_data(path):
    try:
        data = pd.read_excel(path, engine='openpyxl')
    except Exception as excep:
        sys.stderr(
            "Não foi possível fazer a leitura do arquivo: " + path
            + ". O seguinte erro foi gerado:" + str(excep)
        )
        os._exit(1)

    return data

def parse_employees(fn, chave_coleta):
    rows = read_data(fn).to_numpy()
    employees = {}
    counter = 1
    for row in rows:
        name = row[1]
       
        if name != "0":
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + '/' + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = name 
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            membro.remuneracoes.CopyFrom(cria_remuneracao(row, CONTRACHEQUE))
            employees[name] = membro
            counter += 1
    return employees

def cria_remuneracao(row,  categoria):
    remu_array = Coleta.Remuneracoes()
    items = list(HEADERS[categoria].items())
    for i in  range(len(items)):
        key, value = items[i][0], items[i][1]
        if 'Outra' in key:
            remuneracao = Coleta.Remuneracao()
            remuneracao.item = row[items[i+1][1]]
            remuneracao.valor = float(row[value])
            remuneracao.categoria = categoria
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            continue
        elif 'Detalhe' in key:
            continue
        remuneracao = Coleta.Remuneracao()
        remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
        remuneracao.categoria = categoria
        remuneracao.item = key
        remuneracao.valor = float(row[value])
        remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        if categoria == CONTRACHEQUE and value == 3:
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
        if categoria == CONTRACHEQUE and value in [8,9,10,11]:
            remuneracao.valor = remuneracao.valor * (-1)
            remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
        if categoria == DIREITOS_EVENTUAIS and value == 5:
            remuneracao.valor = format_value(row[value])
            
        remu_array.remuneracao.append(remuneracao)
    return remu_array

def update_employees(fn, employees, categoria):
    rows = read_data(fn).to_numpy()
    for row in rows:
        name = row[1]
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees

def isNaN(string):
    return string != string

def parse(file_names, chave_coleta):
    employees = {}
    folha = Coleta.FolhaDePagamento()
    try:
        for fn in file_names:
            if "contracheque" in fn:
                # Puts all parsed employees in the big map
                employees.update(parse_employees(fn, chave_coleta))
            elif "indenizações" in  fn:
                update_employees(fn, employees, INDENIZACOES)
            elif "direitos-eventuais" in fn:
                update_employees(fn, employees, DIREITOS_EVENTUAIS)
            elif "-direitos-pessoais" in fn:
                update_employees(fn, employees, DIREITOS_PESSOAIS)

    except KeyError as e:
        sys.stderr.write(
            "Registro inválido ao processar verbas indenizatórias: {}".format(e)
        )
        os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i) 
    return folha
    #return list(employees.values())

def format_value(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if isNaN(element):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)

