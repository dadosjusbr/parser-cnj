# coding: utf8

import sys
import os

import pandas as pd
from coleta import coleta_pb2 as Coleta
from openpyxl.utils.escape import unescape

from headers_keys import (CONTRACHEQUE, INDENIZACOES, DIREITOS_PESSOAIS,
                          DIREITOS_EVENTUAIS, HEADERS)
import number
import re
from data import STATUS_DATA_UNAVAILABLE, STATUS_INVALID_FILE


sem_detalhamento = False


# Recorte do órgão e do mês, igual em todas as planilhas. O coletor antigo baixava
# junto os tribunais com a mesma sigla no início (tjms/TJMSP, trt1/TRT10 a TRT19,
# trt2/TRT20 a TRT24), então o tribunal precisa ser conferido em todas elas.
def no_recorte(row, court, month, year):
    tribunal, referencia = row[0], row[2]
    if number.is_nan(row[1]) or not isinstance(tribunal, str):
        return False
    return (tribunal.strip().casefold() == court.strip().casefold()
            and str(referencia).strip() == f'{int(month):02}/{year}')

def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    global sem_detalhamento
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

        key, value = row[5], row[4]
        if validate(key, value):
            remuneracao = Coleta.Remuneracao()
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            remuneracao.categoria = categoria
            remuneracao.item = format_item(key)
            remuneracao.valor = number.format_element(value)
            remu_array.remuneracao.append(remuneracao)

            if not bool(re.search('[A-Za-z]', format_item(key))):
                sem_detalhamento = True

        key, value = row[7], row[6]
        if validate(key, value):
            remuneracao = Coleta.Remuneracao()
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            remuneracao.categoria = categoria
            remuneracao.item = format_item(key)
            remuneracao.valor = number.format_element(value)
            remu_array.remuneracao.append(remuneracao)

            if not bool(re.search('[A-Za-z]', format_item(key))):
                sem_detalhamento = True

        return remu_array, sem_detalhamento

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
            if validate(row[10], row[9]):
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = format_item(row[10])
                remuneracao.valor = number.format_element(row[9])
                remu_array.remuneracao.append(remuneracao)

                if not bool(re.search('[A-Za-z]', format_item(row[10]))):
                    sem_detalhamento = True

        elif categoria == INDENIZACOES and value == 11:
            if validate(row[12], row[11]):
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = format_item(row[12])
                remuneracao.valor = number.format_element(row[11])
                remu_array.remuneracao.append(remuneracao)

                if not bool(re.search('[A-Za-z]', format_item(row[12]))):
                    sem_detalhamento = True

        elif categoria == INDENIZACOES and value == 13:
            if validate(row[14], row[13]):
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = format_item(row[14])
                remuneracao.valor = number.format_element(row[13])
                remu_array.remuneracao.append(remuneracao)

                if not bool(re.search('[A-Za-z]', format_item(row[14]))):
                    sem_detalhamento = True

        # Se a coluna 'Outra' ou a coluna 'Detalhe' for diferente de 0, será criada a remuneração.
        elif categoria == DIREITOS_EVENTUAIS and value == 13:
            if validate(row[14], row[13]):
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = format_item(row[14])
                remuneracao.valor = number.format_element(row[13])
                remu_array.remuneracao.append(remuneracao)

                if not bool(re.search('[A-Za-z]', format_item(row[14]))):
                    sem_detalhamento = True

        # Caso seja coluna "Outra" e a coluna "Detalhe" seja diferente de 0,
        # será criada a remuneração.
        elif categoria == DIREITOS_EVENTUAIS and value == 15:
            if validate(row[16], row[15]):
                remuneracao = Coleta.Remuneracao()
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
                remuneracao.categoria = categoria
                remuneracao.item = format_item(row[16])
                remuneracao.valor = number.format_element(row[15])
                remu_array.remuneracao.append(remuneracao)

                if not bool(re.search('[A-Za-z]', format_item(row[16]))):
                    sem_detalhamento = True

        # Cria a remuneração para as demais categorias que não necessitam
        # de tratamento especial para suas colunas "Outra" e "Detalhe"
        else:
            remuneracao = Coleta.Remuneracao()
            remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
            remuneracao.categoria = categoria
            remuneracao.item = key
            remuneracao.valor = number.format_element(row[value])
            if categoria == CONTRACHEQUE and value in [10, 11, 12, 13]:
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
                remuneracao.valor = abs(remuneracao.valor) * (-1)
            else:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            if categoria == CONTRACHEQUE and value == 5:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            remu_array.remuneracao.append(remuneracao)

    return remu_array, sem_detalhamento


def parse_employees(fn, chave_coleta, court, month, year):
    # sem_detalhamento é global para que planilhas sem linhas não deixem a variável indefinida.
    global sem_detalhamento
    employees = {}
    counter = 1
    for row in fn:
        name = row[1]
        # Ignora linhas vazias e linhas de outro órgão ou de outro mês.
        if no_recorte(row, court, month, year):
            if name in (0,'0'):
                sys.stderr.write(f"Dados de contracheque sumarizados.")
                sys.exit(STATUS_DATA_UNAVAILABLE)

            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = str(name)  # Para o caso do campo vier com um int
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            membro.funcao = str(row[3])
            membro.local_trabalho = str(row[4])
            contracheques, sem_detalhamento = cria_remuneracao(
                row, CONTRACHEQUE)
            membro.remuneracoes.CopyFrom(contracheques)
            employees[name] = membro
            counter += 1
    return employees, sem_detalhamento

# Atualiza os dados que foram passados no segundo parâmetro
def update_employees(data, employees, categoria, court, month, year):
    global sem_detalhamento
    for row in data:
        name = row[1]
        if name in employees.keys() and no_recorte(row, court, month, year):
            emp = employees[name]
            remu, sem_detalhamento = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees, sem_detalhamento


def parse(data, chave_coleta):
    employees = {}
    folha = Coleta.FolhaDePagamento()

    try:
        # Cria a base com o contracheque, depois vai ser atualizado com
        # as outras planilhas.
        contracheques, sem_detalhamento = parse_employees(
            data.contracheque, chave_coleta, data.court, data.month, data.year)
        employees.update(contracheques)
        # Sem nenhuma linha do órgão e do mês, o arquivo não corresponde ao pedido
        # (formato mudou, outro tribunal, outro mês). Não pode virar coleta vazia com sucesso.
        if not employees:
            sys.stderr.write(f"Nenhuma linha de {data.court} {data.month}/{data.year} no contracheque.")
            sys.exit(STATUS_INVALID_FILE)

        _, sem_detalhamento = update_employees(
            data.indenizacoes, employees, INDENIZACOES, data.court, data.month, data.year)

        _, sem_detalhamento = update_employees(
            data.direitos_eventuais, employees, DIREITOS_EVENTUAIS, data.court, data.month, data.year)

        _, sem_detalhamento = update_employees(
            data.direitos_pessoais, employees, DIREITOS_PESSOAIS, data.court, data.month, data.year)

    except KeyError as error:
        sys.stderr.write(
            f"Registro inválido ao processar verbas indenizatórias: {error}"
        )
        os._exit(1)
    except ValueError as error:
        sys.stderr.write(f"Valor que não pôde ser lido como número: {error}")
        sys.exit(STATUS_INVALID_FILE)

    for values in employees.values():
        folha.contra_cheque.append(values)
    return folha, sem_detalhamento


# O xlsx grava caracteres de controle como '_xHHHH_' (ex.: '_x000D_' é o CR).
# O openpyxl não desfaz esse escape na leitura; aqui o valor volta a ser o original.
def format_item(item):
    return unescape(str(item))

def validate(key, value) -> bool:
    if str(key) not in ['0', '0.0', '-'] or str(value) not in ['0', '0.0', '-']:
        return True
    else:
        return False

# Em abril/2023 percebemos que alguns órgãos têm colocado o valor na coluna 'Detalhe'
# e não informando a descrição do respectivo gasto
# Alguns órgãos tbm têm colocado o valor na própria coluna, 'Outra', mas tbm não informando o 'Detalhe'
# Ainda outros têm colocado o valor da remuneração em ambas colunas.
# Nesses casos, consideramos o valor e recebemos "NÃO INFORMADO" como item
# Em junho/2023, decidimos manter as planilhas com os erros de detalhamento.
# Portanto, essa função não está mais sendo utilizada, estando aqui para posteriores consultas.
def check_details(key, value):
    global sem_detalhamento
    item = "NÃO INFORMADO"
    if str(key) in ['0', '0.0', '-'] or str(key).replace(",", ".") == str(value):
        try:
            valor = number.format_element(value)
            sem_detalhamento = True
        except:
            pass
    elif str(value) in ['0', '0.0', '-'] and not bool(re.search('[A-Za-z]', str(key))):
        valor = number.format_element(key)
        sem_detalhamento = True
    else:
        item = str(key)
        valor = number.format_element(value)
    return item, valor