"""Estrutura editorial compartilhada pelos geradores."""

import re

NIVEIS = {"titulo": 1, "subtitulo": 2, "secao_nivel_3": 3}


def preparar_conteudo(blocos):
    """Separa conteúdo, sumário e referências sem exigir manutenção duplicada."""
    conteudo, referencias, vistos = [], [], set()
    for bloco in blocos:
        if bloco["tipo"] == "bibliografia":
            candidatos = bloco["itens"]
        elif bloco["tipo"] == "link":
            candidatos = [{"titulo": bloco["texto"], "url": bloco["url"]}]
            conteudo.append(dict(bloco))
        else:
            conteudo.append(dict(bloco))
            continue
        for item in candidatos:
            chave = (item.get("url", ""), item["titulo"].strip().lower())
            if chave not in vistos:
                referencias.append(dict(item)); vistos.add(chave)
    sumario = _numerar_sumario(conteudo)
    if referencias:
        proximo = sum(1 for item in sumario if item["nivel"] == 1) + 1
        sumario.append({"nivel": 1, "numero": str(proximo), "texto": "Referências"})
    for numero, bloco in enumerate((b for b in conteudo if b["tipo"] in {"imagem", "diagrama_mermaid", "diagrama_bpmn"}), start=1):
        bloco["_numero_figura"] = numero
    return conteudo, sumario, referencias


def _numerar_sumario(blocos):
    contadores = [0, 0, 0]
    itens = []
    for bloco in blocos:
        if bloco["tipo"] not in NIVEIS:
            continue
        nivel = NIVEIS[bloco["tipo"]]
        contadores[nivel - 1] += 1
        for indice in range(nivel, len(contadores)):
            contadores[indice] = 0
        numero = ".".join(str(valor) for valor in contadores[:nivel])
        texto = re.sub(r"^\s*\d+(?:\.\d+)*\.?\s*", "", bloco["texto"])
        itens.append({"nivel": nivel, "numero": numero, "texto": texto})
    return itens
