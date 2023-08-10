from coleta import coleta_pb2 as Coleta


def captura(sem_detalhamento: bool):
    metadado = Coleta.Metadados()
    metadado.acesso = Coleta.Metadados.FormaDeAcesso.NECESSITA_SIMULACAO_USUARIO
    metadado.extensao = Coleta.Metadados.Extensao.XLS
    metadado.estritamente_tabular = True
    metadado.formato_consistente = True
    metadado.tem_matricula = False
    metadado.tem_lotacao = True
    metadado.tem_cargo = True
    metadado.receita_base = Coleta.Metadados.OpcoesDetalhamento.DETALHADO
    metadado.despesas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO
    if sem_detalhamento == True:
        metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.SUMARIZADO
    else:
        metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO

    return metadado
