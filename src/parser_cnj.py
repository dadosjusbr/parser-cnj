# coding: utf8

import sys
import os

import pandas as pd
from coleta import coleta_pb2 as Coleta

from headers_keys import (CONTRACHEQUE, INDENIZACOES, DIREITOS_PESSOAIS,
                          DIREITOS_EVENTUAIS, HEADERS)
import number


def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    """
    Caso especial para categoria Direitos Pessoais.
    Caso a coluna Detalhe tenha valor diferente de 0,
    a coluna Outras recebe esse valor para o parametro "item" 
    e mantém seu valor para o parametro "valor".
    """
    if categoria == DIREITOS_PESSOAIS:
        key, value = "Abono de permanência", row[3]
        remuneracao = Coleta.Remuneracao()
        remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        remuneracao.item = key
        remuneracao.valor = number.format_element(value)
        remuneracao.categoria = categoria
        remu_array.remuneracao.append(remuneracao)

        key, value = str(row[5]), row[4]
        if key != '0' and key != '0.0' and key != '-':
            remuneracao = Coleta.Remuneracao()
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            remuneracao.item = key
            remuneracao.valor = number.format_element(value)
            remuneracao.categoria = categoria
            remu_array.remuneracao.append(remuneracao)

        key, value = str(row[7]), row[6]
        if key != '0' and key != '0.0' and key != '-':
            remuneracao = Coleta.Remuneracao()
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            remuneracao.item = key
            remuneracao.valor = number.format_element(value)
            remuneracao.categoria = categoria
            remu_array.remuneracao.append(remuneracao)

        return remu_array


    items = list(HEADERS[categoria].items())
    for i in range(len(items)):
        key, value = items[i][0], items[i][1]
        # Campo da coluna "Detalhe", que só utilizado para valor da coluna "Outra".
        if categoria == DIREITOS_EVENTUAIS and value in [14, 16]:
            continue
        # Campo da coluna "Detalhe", não está sendo utilizado para indenizações.
        if categoria == INDENIZACOES and value in [10, 12, 14]:
            continue
        if categoria == INDENIZACOES and value == 9:
            if str(row[10]) != '0' and str(row[10]) != '0.0' and str(row[10]) != '-':
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = row[10]
                remuneracao.valor = number.format_element(row[9])
                remu_array.remuneracao.append(remuneracao)
        elif categoria == INDENIZACOES and value == 11:
            if str(row[12]) != '0' and str(row[12]) != '0.0' and str(row[12]) != '-':
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = row[12]
                remuneracao.valor = number.format_element(row[11])
                remu_array.remuneracao.append(remuneracao)
        elif categoria == INDENIZACOES and value == 13:
            if str(row[14]) != '0' and str(row[14]) != '0.0' and str(row[14]) != '-':
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = row[14]
                remuneracao.valor = number.format_element(row[13])
                remu_array.remuneracao.append(remuneracao)
        # Caso seja coluna "Outra" e a coluna "Detalhe" seja diferente de 0, será criada a remuneração.
        elif categoria == DIREITOS_EVENTUAIS and value == 13:
            if str(row[14]) != '0' and str(row[14]) != '0.0' and str(row[14]) != '-':
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = str(row[14])
                remuneracao.valor = number.format_element(row[13])
                remu_array.remuneracao.append(remuneracao)
        # Caso seja coluna "Outra" e a coluna "Detalhe" seja diferente de 0,
        # será criada a remuneração.
        elif categoria == DIREITOS_EVENTUAIS and value == 15:
            if str(row[16]) != '0' and str(row[16]) != '0.0' and str(row[16]) != '-':
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = str(row[16])
                remuneracao.valor = number.format_element(row[15])
                remu_array.remuneracao.append(remuneracao)
        # Cria a remuneração para as demais categorias que não necessitam 
        # de tratamento especial para suas colunas "Outra" e "Detalhe"
        else:
            remuneracao = Coleta.Remuneracao()
            remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
            remuneracao.categoria = categoria
            remuneracao.item = key
            remuneracao.valor = number.format_element(row[value])
            if categoria == CONTRACHEQUE and value in [8, 9, 10, 11]:
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
                remuneracao.valor = remuneracao.valor * (-1)
            else:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            if categoria == CONTRACHEQUE and value == 3:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            remu_array.remuneracao.append(remuneracao)

    return remu_array


def parse_employees(fn, chave_coleta):
    employees = {}
    counter = 1
    for row in fn:
        name = row[1]
        # Usa-se o isNaN para não pegar linhas vázias.
        if not number.is_nan(name):
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = str(name)  # Para o caso do campo vier com um int
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            membro.remuneracoes.CopyFrom(cria_remuneracao(row, CONTRACHEQUE))
            employees[name] = membro
            counter += 1
    return employees

# Atualiza os dados que foram passados no segundo parâmetro
def update_employees(data, employees, categoria):
    for row in data:
        name = row[1]
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees


def parse(data, chave_coleta):
    employees = {}
    folha = Coleta.FolhaDePagamento()

    try:
        # Cria a base com o contracheque, depois vai ser atualizado com 
        # as outras planilhas.
        employees.update(parse_employees(data.contracheque, chave_coleta))

        update_employees(data.indenizacoes, employees, INDENIZACOES)
        update_employees(data.direitos_eventuais, employees, DIREITOS_EVENTUAIS)
        update_employees(data.direitos_pessoais, employees, DIREITOS_PESSOAIS)

    except KeyError as error:
        sys.stderr.write(
                f"Registro inválido ao processar verbas indenizatórias: {error}"
            )
        os._exit(1)

    for values in employees.values():
        folha.contra_cheque.append(values)
    return folha
