"""Conversor Markdown deliberadamente pequeno e previsível para o contrato interno."""

import re


def converter_markdown_para_json(markdown_text):
    blocos, paragrafo, lista, codigo = [], [], [], []
    linguagem = None

    def descarregar_texto():
        nonlocal paragrafo
        if paragrafo:
            blocos.append({"tipo": "texto", "texto": " ".join(paragrafo)})
            paragrafo = []

    def descarregar_lista():
        nonlocal lista
        if lista:
            blocos.append({"tipo": "lista", "itens": lista})
            lista = []

    for linha in markdown_text.splitlines():
        limpa = linha.strip()
        if limpa.startswith("```"):
            if linguagem is None:
                descarregar_texto(); descarregar_lista(); linguagem = limpa[3:].strip().lower(); codigo = []
            else:
                chave = "codigo" if linguagem == "mermaid" else "texto"
                blocos.append({"tipo": "diagrama_mermaid" if linguagem == "mermaid" else "codigo", chave: "\n".join(codigo)})
                linguagem, codigo = None, []
            continue
        if linguagem is not None:
            codigo.append(linha); continue
        if not limpa:
            descarregar_texto(); descarregar_lista(); continue
        cabecalho = re.match(r"^(#{1,3})\s+(.+)$", limpa)
        if cabecalho:
            descarregar_texto(); descarregar_lista()
            nivel, texto = len(cabecalho.group(1)), cabecalho.group(2)
            blocos.append({"tipo": ("titulo", "subtitulo", "secao_nivel_3")[nivel - 1], "texto": texto}); continue
        imagem = re.match(r"^!\[(.*?)\]\((.*?)\)$", limpa)
        if imagem:
            descarregar_texto(); descarregar_lista(); legenda, caminho = imagem.groups()
            blocos.append({"tipo": "imagem", "caminho": caminho.strip(), "legenda": legenda.strip()}); continue
        fonte = re.match(r"^(?:\*\*)?Fonte:(?:\*\*)?\s*(.+)$", limpa, flags=re.IGNORECASE)
        if fonte and blocos and blocos[-1]["tipo"] == "imagem":
            blocos[-1]["fonte"] = fonte.group(1).strip(); continue
        link = re.match(r"^\[(.*?)\]\((https?://.*?)\)$", limpa)
        if link:
            descarregar_texto(); descarregar_lista(); texto, url = link.groups()
            blocos.append({"tipo": "link", "texto": texto, "url": url}); continue
        if limpa.startswith("> "):
            descarregar_texto(); descarregar_lista(); blocos.append({"tipo": "callout", "texto": limpa[2:]}); continue
        item = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", limpa)
        if item:
            descarregar_texto(); lista.append(item.group(1)); continue
        descarregar_lista(); paragrafo.append(limpa)
    if linguagem is not None:
        raise ValueError("Bloco de código Markdown sem fechamento (```).")
    descarregar_texto(); descarregar_lista()
    return {"secoes": blocos}
