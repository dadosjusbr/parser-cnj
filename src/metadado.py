from coleta import coleta_pb2 as Coleta


def captura(resultado_coleta):
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

    completude_receita_base = 0
    completude_outras_receitas = 0
    completude_despesa = 0
    for remuneracao in resultado_coleta.folha.contra_cheque[0].remuneracoes.remuneracao:
        if remuneracao.categoria == "contracheque":
            if remuneracao.valor > 0.0:
                completude_receita_base += 1
            else:
                completude_despesa += 1
        else:
            completude_outras_receitas += 1

    if completude_receita_base == 0:
        metadado.receita_base = Coleta.Metadados.OpcoesDetalhamento.AUSENCIA
    elif completude_receita_base == 1:
        metadado.receita_base = Coleta.Metadados.OpcoesDetalhamento.SUMARIZADO
    else:
        metadado.receita_base = Coleta.Metadados.OpcoesDetalhamento.DETALHADO

    if completude_outras_receitas == 0:
        metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.AUSENCIA
    elif completude_outras_receitas == 1:
        metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.SUMARIZADO
    else:
        metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO

    if completude_despesa == 0:
        metadado.despesas = Coleta.Metadados.OpcoesDetalhamento.AUSENCIA
    elif completude_despesa == 1:
        metadado.despesas = Coleta.Metadados.OpcoesDetalhamento.SUMARIZADO
    else:
        metadado.despesas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO

    resultado_coleta.metadados.CopyFrom(metadado)
    return resultado_coleta