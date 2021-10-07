from coleta import coleta_pb2 as Coleta
import pandas as pd
import sys
import os

DETALHADO = Coleta.Metadados.OpcoesDetalhamento.DETALHADO
SUMARIZADO = Coleta.Metadados.OpcoesDetalhamento.SUMARIZADO
AUSENCIA = Coleta.Metadados.OpcoesDetalhamento.AUSENCIA


def read_data(path):
    try:
        data = pd.read_excel(path, engine="openpyxl")
    except Exception as excep:
        sys.stderr(
            "Não foi possível fazer a leitura do arquivo: "
            + path
            + ". O seguinte erro foi gerado:"
            + str(excep)
        )
        os._exit(1)

    return data


def captura(fn):
    metadado = Coleta.Metadados()
    metadado.nao_requer_login = True
    metadado.nao_requer_captcha = True
    metadado.acesso = Coleta.Metadados.FormaDeAcesso.NECESSITA_SIMULACAO_USUARIO
    metadado.extensao = Coleta.Metadados.Extensao.XLS
    metadado.estritamente_tabular = True
    metadado.formato_consistente = True
    metadado.tem_matricula = False
    metadado.tem_lotacao = False
    metadado.tem_cargo = False

    for file in fn:
        if "contracheque" in file:
            rows = read_data(file)
            if rows["Subsídio (R$)"].any():
                metadado.receita_base = DETALHADO
            else:
                metadado.receita_base = AUSENCIA

            if (
                rows["Previdência Pública (5) (R$)"].any()
                and rows["Imposto de Renda (6) (R$)"].any()
                and rows["Retenção por Teto Constitucional (8) (R$)"].any()
            ):
                metadado.despesas = DETALHADO
            elif (
                rows["Previdência Pública (5) (R$)"].any()
                or rows["Imposto de Renda (6) (R$)"].any()
                or rows["Retenção por Teto Constitucional (8) (R$)"].any()
            ):
                metadado.despesas = SUMARIZADO
            else:
                metadado.despesas = AUSENCIA
        elif "indenizações" in file:
            rows = read_data(file)
            if (
                rows["Auxílio-alimentação (R$)"].any()
                and rows["Auxílio Pré-escolar (R$)"].any()
                and rows["Auxílio Saúde (R$)"].any()
                and rows["Auxílio Natalidade (R$)"].any()
                and rows["Auxílio Moradia (R$)"].any()
            ):
                metadado.outras_receitas = DETALHADO
            elif (
                rows["Auxílio-alimentação (R$)"].any()
                or rows["Auxílio Pré-escolar (R$)"].any()
                or rows["Auxílio Saúde (R$)"].any()
                or rows["Auxílio Natalidade (R$)"].any()
                or rows["Auxílio Moradia (R$)"].any()
            ):
                metadado.outras_receitas = SUMARIZADO
            else:
                metadado.outras_receitas = AUSENCIA

    return metadado
