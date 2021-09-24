# coding: utf8
import sys
import os
import crawler
import time
from parserr import parse
import json
from coleta import coleta_pb2 as Coleta, IDColeta
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToDict


if('COURT' in os.environ):
    court = os.environ['COURT']
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'COURT'.\n")
    os._exit(1)
if('YEAR' in os.environ):
    year = os.environ['YEAR']
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'YEAR'.\n")
    os._exit(1)
if('MONTH' in os.environ):
    month = os.environ['MONTH']
    month = month.zfill(2)
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'MONTH'.\n")
    os._exit(1)
if('DRIVER_PATH' in os.environ):
    driver_path = os.environ['DRIVER_PATH']
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'DRIVER_PATH'.\n")
    os._exit(1)
if('OUTPUT_FOLDER' in os.environ):
    output_path = os.environ['OUTPUT_FOLDER']
else:
    output_path = "./output"
if('GIT_COMMIT' in os.environ):
    crawler_version = os.environ['GIT_COMMIT']
else:
    sys.stderr.write("crawler_version cannot be empty")
    os._exit(1)

repColetor = "https://github.com/dadosjusbr/coletores"

# Main execution
def main():
    file_names = crawler.crawl(court, year, month, driver_path, output_path)
    coleta = Coleta.Coleta()
    coleta.chave_coleta = IDColeta(court, month, year)
    folha = Coleta.FolhaDePagamento()
    folha = parse(file_names, coleta.chave_coleta)
    coleta.orgao = court.lower()
    coleta.mes = int(month)
    coleta.ano = int(year)
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    coleta.timestamp_coleta.CopyFrom(timestamp)
    coleta.repositorio_coletor = repColetor
    coleta.versao_coletor = crawler_version
    coleta.dir_coletor = 'cnj'
    coleta.arquivos.extend(file_names)
    rc = {
        'coleta': coleta,
        'folha': folha,
    }
    rc = Coleta.ResultadoColeta()
    rc.folha.CopyFrom(folha)
    rc.coleta.CopyFrom(coleta)
    print(rc.SerializeToString())
    #rc_dict = MessageToDict(rc, preserving_proto_field_name=True, use_integers_for_enums= True)
    #print(json.dumps({'coleta': rc_dict['coleta'], 'folha': rc_dict['folha']}, ensure_ascii=False))
    

if __name__ == '__main__':
    main()

def MessageToDict(message):
    messageDict = {}

    for descriptor in message.DESCRIPTOR.fields:
        key = descriptor.name
        value = getattr(message, descriptor.name)

        if descriptor.label == descriptor.LABEL_REPEATED:
            messageList = []

            for subMessage in value:
                if descriptor.type == descriptor.TYPE_MESSAGE:
                    messageList.append(MessageToDict(subMessage))
                else:
                    messageList.append(subMessage)

            messageDict[key] = messageList
        else:
            if descriptor.type == descriptor.TYPE_MESSAGE:
                messageDict[key] = MessageToDict(value)
            else:
                messageDict[key] = value

    return messageDict