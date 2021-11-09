# coding: utf8
import pandas as pd
import sys
import os
from  coleta import coleta_pb2 as Coleta

CONTRACHEQUE = 'contracheque'
INDENIZACOES = 'indenizações'
DIREITOS_EVENTUAIS = 'direitos-eventuais'
DIREITOS_PESSOAIS = 'direitos-pessoais'
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


def parse_employees(fn, chave_coleta):
    employees = {}
    counter = 1
    for row in fn:
        name = row[1]
        # Usa-se o isNaN para não pegar linhas vázias.
        if not isNaN(name):
                membro = Coleta.ContraCheque()
                membro.id_contra_cheque = chave_coleta + '/' + str(counter)
                membro.chave_coleta = chave_coleta
                membro.nome = str(name) # Para o caso do campo vier com um int 
                membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
                membro.ativo = True
                membro.remuneracoes.CopyFrom(cria_remuneracao(row, CONTRACHEQUE))
                employees[name] = membro
                counter += 1
    return employees


def cria_remuneracao(row,  categoria):
    remu_array = Coleta.Remuneracoes()
    if categoria == DIREITOS_PESSOAIS:
        key, value = 'Abono de permanência', row[3]
        remuneracao = Coleta.Remuneracao()
        remuneracao.item = key
        remuneracao.valor = float(format_value(value))
        remuneracao.categoria = categoria
        remu_array.remuneracao.append(remuneracao)

        key, value = row[5], row[4]       
        if key != '0':
            remuneracao = Coleta.Remuneracao()
            remuneracao.item = key
            remuneracao.valor = float(format_value(value))
            remuneracao.categoria = categoria
            remu_array.remuneracao.append(remuneracao)
        
        key, value = row[7], row[6]       
        if key != '0':
            remuneracao = Coleta.Remuneracao()
            remuneracao.item = key
            remuneracao.valor = float(format_value(value))
            remuneracao.categoria = categoria
            remu_array.remuneracao.append(remuneracao)

        return remu_array
        
    # 
    items = list(HEADERS[categoria].items())
    for i in  range(len(items)):
        key, value = items[i][0], items[i][1]
        if value in [14, 16]:
            continue
        if categoria == DIREITOS_EVENTUAIS and value == 13:
            if row[14] != 0:
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.categoria = categoria
                remuneracao.item = row[14]
                remuneracao.valor = float(format_value(row[13]))
                remu_array.remuneracao.append(remuneracao)
        elif categoria == DIREITOS_EVENTUAIS and value == 15:
            if row[16] != 0:
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.categoria = categoria
                remuneracao.item = row[16]
                remuneracao.valor = float(format_value(row[15]))
                remu_array.remuneracao.append(remuneracao)
        else:
            remuneracao = Coleta.Remuneracao()
            remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
            remuneracao.categoria = categoria
            remuneracao.item = key
            remuneracao.valor = float(format_value(row[value]))
            if categoria == CONTRACHEQUE and value in [8,9,10,11]:
                remuneracao.valor = remuneracao.valor * (-1)
            remu_array.remuneracao.append(remuneracao)
        
            
    return remu_array

def update_employees(fn, employees, categoria):
    for row in fn:
        name = row[1]
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees


def isNaN(string):
    return string != string


def parse(data, chave_coleta):
    employees = {}
    folha = Coleta.FolhaDePagamento()

    try:
        employees.update(parse_employees(data.contracheque, chave_coleta))
        update_employees(data.indenizacoes, employees, INDENIZACOES)
        update_employees(data.direitos_eventuais, employees, DIREITOS_EVENTUAIS)
        update_employees(data.direitos_pessoais, employees, DIREITOS_PESSOAIS)
                
    except KeyError as e:
        sys.stderr.write(
            f"Registro inválido ao processar verbas indenizatórias: {e}"
        )
        os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i) 
    return folha



