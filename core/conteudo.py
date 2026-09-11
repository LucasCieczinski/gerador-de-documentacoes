"""Contrato, validação e normalização do conteúdo da documentação."""

import json
from pathlib import Path
from urllib.parse import urlparse

TIPOS_VALIDOS = {
    "titulo", "subtitulo", "secao_nivel_3", "texto", "codigo", "imagem",
    "diagrama_mermaid", "diagrama_bpmn", "link", "lista", "tabela", "callout", "bibliografia",
}


class ConteudoInvalido(ValueError):
    """Erro de validação do arquivo de conteúdo."""


def carregar_conteudo(caminho_json):
    """Carrega um JSON, resolve recursos relativos e retorna blocos normalizados."""
    caminho = Path(caminho_json)
    if not caminho.is_file():
        raise ConteudoInvalido(f"Arquivo não encontrado: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ConteudoInvalido(f"JSON inválido em '{caminho}': {erro}") from erro
    if not isinstance(dados, dict) or not isinstance(dados.get("secoes"), list):
        raise ConteudoInvalido("O JSON precisa conter a chave 'secoes' com uma lista de blocos.")
    return normalizar_blocos(dados["secoes"], caminho.parent)


def normalizar_blocos(blocos, pasta_base):
    """Valida blocos de qualquer origem e resolve imagens contra ``pasta_base``."""
    if not isinstance(blocos, list):
        raise ConteudoInvalido("As seções precisam ser uma lista.")
    normalizados = []
    for indice, bloco in enumerate(blocos, start=1):
        if not isinstance(bloco, dict):
            raise ConteudoInvalido(f"Seção {indice}: precisa ser um objeto.")
        bloco = dict(bloco)
        tipo = bloco.get("tipo")
        if tipo not in TIPOS_VALIDOS:
            raise ConteudoInvalido(f"Seção {indice}: tipo inválido '{tipo}'.")
        if tipo in {"titulo", "subtitulo", "secao_nivel_3", "texto", "codigo", "callout"}:
            _texto(bloco, "texto", indice, tipo)
        elif tipo == "lista":
            itens = bloco.get("itens")
            if not isinstance(itens, list) or not itens or not all(isinstance(item, str) for item in itens):
                raise ConteudoInvalido(f"Seção {indice} (lista): 'itens' deve ser uma lista não vazia de textos.")
        elif tipo == "imagem":
            caminho = bloco.get("caminho")
            if not isinstance(caminho, str) or not caminho.strip():
                raise ConteudoInvalido(f"Seção {indice} (imagem): 'caminho' é obrigatório.")
            resolvido = (Path(pasta_base) / caminho).resolve() if not Path(caminho).is_absolute() else Path(caminho)
            if not resolvido.is_file():
                raise ConteudoInvalido(f"Seção {indice} (imagem): arquivo não encontrado: {resolvido}")
            bloco["caminho"] = str(resolvido)
            bloco["fonte"] = _fonte(bloco, indice, tipo)
        elif tipo in {"diagrama_mermaid", "diagrama_bpmn"}:
            _texto(bloco, "codigo", indice, tipo)
            bloco["fonte"] = _fonte(bloco, indice, tipo)
        elif tipo == "link":
            _texto(bloco, "texto", indice, tipo)
            url = bloco.get("url")
            if not isinstance(url, str) or urlparse(url).scheme not in {"http", "https"}:
                raise ConteudoInvalido(f"Seção {indice} (link): informe uma URL http(s) válida.")
        elif tipo == "bibliografia":
            itens = bloco.get("itens")
            if not isinstance(itens, list) or not itens:
                raise ConteudoInvalido(f"Seção {indice} (bibliografia): 'itens' deve ser uma lista não vazia.")
            for item in itens:
                if not isinstance(item, dict) or not isinstance(item.get("titulo"), str) or not item["titulo"].strip():
                    raise ConteudoInvalido(f"Seção {indice} (bibliografia): cada item precisa de 'titulo'.")
                if item.get("url") and (not isinstance(item["url"], str) or urlparse(item["url"]).scheme not in {"http", "https"}):
                    raise ConteudoInvalido(f"Seção {indice} (bibliografia): URL inválida.")
        elif tipo == "tabela":
            bloco["cabecalhos"] = bloco.get("cabecalhos", bloco.get("colunas"))
            cabecalhos, linhas = bloco["cabecalhos"], bloco.get("linhas")
            if not isinstance(cabecalhos, list) or not cabecalhos or not all(isinstance(x, str) for x in cabecalhos):
                raise ConteudoInvalido(f"Seção {indice} (tabela): 'cabecalhos' deve ser uma lista de textos.")
            if not isinstance(linhas, list) or not all(isinstance(linha, list) and len(linha) == len(cabecalhos) for linha in linhas):
                raise ConteudoInvalido(f"Seção {indice} (tabela): cada linha deve ter {len(cabecalhos)} colunas.")
            bloco["linhas"] = [[str(celula) for celula in linha] for linha in linhas]
        normalizados.append(bloco)
    return normalizados


def _texto(bloco, campo, indice, tipo):
    if not isinstance(bloco.get(campo), str) or not bloco[campo].strip():
        raise ConteudoInvalido(f"Seção {indice} ({tipo}): '{campo}' precisa ser um texto não vazio.")


def _fonte(bloco, indice, tipo):
    fonte = bloco.get("fonte", "Elaborado pelo autor.")
    if not isinstance(fonte, str) or not fonte.strip():
        raise ConteudoInvalido(f"Seção {indice} ({tipo}): 'fonte' precisa ser um texto não vazio.")
    return fonte.strip()
