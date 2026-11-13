import re

def is_nan(string):
    return string != string

def format_element(element):
    """Converte o valor da planilha em float.

    O painel novo entrega números. O painel antigo entregava parte dos valores como texto,
    em formato brasileiro ('1234,56', '-24035', '0'), e às vezes 'R$  -' para zero.
    Texto com dígito que não vira número levanta ValueError.
    """
    if is_nan(element):
        return 0.0
    if not isinstance(element, str):
        return float(element)
    texto = element.replace("R$", "").replace(" ", "").strip()
    if not re.search(r'\d', texto):
        return 0.0  # '-', 'R$  -', vazio
    if "," in texto and "." in texto:
        # O último separador é o decimal: '1.234,56' (BR) ou '3,045.99' (EUA).
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    # Sem vírgula, o texto já está no formato do float ('-24035', '1234.5').
    # Antes, qualquer texto com '-' virava 0, o que zerava estornos como '-24035'.
    return float(texto)
