"""Renderização de diagramas Mermaid em imagens PNG.

Tenta primeiro renderizar localmente com o Mermaid CLI (`mmdc`), que é mais
rápido e funciona offline. Se o `mmdc` não estiver instalado (ou falhar), cai
para a API pública do mermaid.ink — nesse caso é necessário ter internet.
"""

import base64
import os
import shutil
import subprocess
import tempfile

import requests


def renderizar_diagrama(codigo_mermaid, caminho_saida_png):
    """Renderiza o código Mermaid em um PNG. Retorna True em caso de sucesso."""
    if shutil.which("mmdc") and _renderizar_local(codigo_mermaid, caminho_saida_png):
        return True

    return _renderizar_online(codigo_mermaid, caminho_saida_png)


def _renderizar_local(codigo_mermaid, caminho_saida_png):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(codigo_mermaid)
            tmp_path = tmp.name

        subprocess.run(
            ["mmdc", "-i", tmp_path, "-o", caminho_saida_png, "-b", "white", "-s", "2"],
            check=True,
            capture_output=True,
        )
        return os.path.isfile(caminho_saida_png)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _renderizar_online(codigo_mermaid, caminho_saida_png):
    try:
        codificado = base64.urlsafe_b64encode(codigo_mermaid.encode("utf-8")).decode("ascii")
        url = f"https://mermaid.ink/img/{codificado}?bgColor=white"
        resposta = requests.get(url, timeout=15)
        resposta.raise_for_status()
        with open(caminho_saida_png, "wb") as f:
            f.write(resposta.content)
        return True
    except requests.RequestException:
        return False