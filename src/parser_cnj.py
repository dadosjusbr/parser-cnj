# coding: utf8

import sys
import os

import pandas as pd
from coleta import coleta_pb2 as Coleta
from openpyxl.utils.escape import unescape

from headers_keys import (CONTRACHEQUE, INDENIZACOES, DIREITOS_PESSOAIS,
                          DIREITOS_EVENTUAIS, HEADERS, TOTAL_NO_CONTRACHEQUE,
                          TOTAL_DA_CATEGORIA)
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
            # Um mesmo nome pode ter mais de um vínculo no mês (ex.: desembargador e
            # pensionista). Cada linha vira um contracheque; employees guarda, por nome,
            # a lista de vínculos com a linha original de cada um.
            employees.setdefault(name, []).append((membro, row))
            counter += 1
    return employees, sem_detalhamento


def total(valor):
    return round(number.format_element(valor), 2)


# Escolhe o vínculo que recebe a linha de uma planilha de categoria quando o nome se repete.
# 1) o vínculo livre cujo total da categoria no contracheque é igual ao total da linha;
# 2) se o total da linha é a soma de todos os vínculos, o painel juntou os vínculos numa
#    linha só: ela fica no primeiro vínculo;
# 3) senão, segue a ordem das linhas.
def escolhe_vinculo(row, vinculos, categoria, usados):
    total_linha = total(row[TOTAL_DA_CATEGORIA[categoria]])
    totais = [total(cc_row[TOTAL_NO_CONTRACHEQUE[categoria]]) for _, cc_row in vinculos]
    livres = [i for i in range(len(vinculos)) if i not in usados]
    for i in livres:
        if abs(totais[i] - total_linha) < 0.01:
            return i
    if total_linha != 0 and abs(sum(totais) - total_linha) < 0.01:
        sys.stderr.write(f"Aviso: {row[1]} ({categoria}) tem uma linha só para {len(vinculos)} vínculos.\n")
        return 0
    if total_linha != 0:
        sys.stderr.write(f"Aviso: {row[1]} ({categoria}) associado pela ordem das linhas.\n")
    return livres[0] if livres else 0


# Acrescenta aos contracheques os itens de uma planilha de categoria.
def update_employees(data, employees, categoria, court, month, year):
    global sem_detalhamento
    usados = {}
    for row in data:
        name = row[1]
        if not no_recorte(row, court, month, year):
            continue
        if name not in employees:
            sys.stderr.write(f"Aviso: {name} está em {categoria} e não está no contracheque.\n")
            continue
        vinculos = employees[name]
        i = 0
        if len(vinculos) > 1:
            i = escolhe_vinculo(row, vinculos, categoria, usados.setdefault(name, set()))
            usados[name].add(i)
        remu, sem_detalhamento = cria_remuneracao(row, categoria)
        vinculos[i][0].remuneracoes.MergeFrom(remu)
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

    for vinculos in employees.values():
        for membro, _ in vinculos:
            folha.contra_cheque.append(membro)
    # Mantém a ordem das linhas da planilha; o armazenador numera os contracheques por posição.
    folha.contra_cheque.sort(key=lambda m: int(m.id_contra_cheque.split("/")[-1]))
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