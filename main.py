"""CLI para geração padronizada de documentação em Word e PDF."""

import argparse
from datetime import date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from core.conteudo import ConteudoInvalido, carregar_conteudo, normalizar_blocos
from core.diagramas import renderizar_diagrama
from core.markdown_parser import converter_markdown_para_json
from core.pdf import gerar_pdf
from core.word import gerar_docx

console = Console()


def slugificar(texto):
    import re
    import unicodedata
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", sem_acentos).strip("-").lower() or "projeto"


def coletar_metadados():
    nome = Prompt.ask("[yellow]Nome do projeto[/yellow]").strip()
    while not nome:
        console.print("[red][ERRO] O nome do projeto não pode ficar em branco.[/red]")
        nome = Prompt.ask("[yellow]Nome do projeto[/yellow]").strip()
    return {"nome_projeto": nome, "descricao": Prompt.ask("[yellow]Breve descrição[/yellow]"),
            "organizacao": Prompt.ask("[yellow]Organização (opcional)[/yellow]", default=""),
            "tipo_documento": Prompt.ask("[yellow]Tipo de documento[/yellow]", default="Documentação Técnica"),
            "cidade": Prompt.ask("[yellow]Cidade[/yellow]", default="São Paulo"),
            "autor": Prompt.ask("[yellow]Autor / equipe[/yellow]", default="Equipe de Desenvolvimento"),
            "versao": Prompt.ask("[yellow]Versão[/yellow]", default="1.0.0"),
            "classificacao": Prompt.ask("[yellow]Classificação[/yellow]", default="Uso interno"),
            "data_criacao": date.today().strftime("%d/%m/%Y")}


def carregar_entrada(caminho):
    caminho = Path(caminho).resolve()
    if caminho.suffix.lower() == ".json":
        return carregar_conteudo(caminho)
    if caminho.suffix.lower() == ".md":
        markdown = converter_markdown_para_json(caminho.read_text(encoding="utf-8"))
        return normalizar_blocos(markdown["secoes"], caminho.parent)
    raise ConteudoInvalido("A entrada deve ter extensão .json ou .md.")


def processar_diagramas(blocos, pasta_assets):
    diagramas = [bloco for bloco in blocos if bloco["tipo"] in {"diagrama_mermaid", "diagrama_bpmn"}]
    if not diagramas:
        return
    pasta_assets.mkdir(parents=True, exist_ok=True)
    for indice, bloco in enumerate(diagramas, start=1):
        prefixo = "bpmn" if bloco["tipo"] == "diagrama_bpmn" else "diagrama"
        caminho = pasta_assets / f"{prefixo}-{indice}.png"
        console.print(f"[blue][...] Renderizando diagrama {indice}/{len(diagramas)}...[/blue]")
        if not renderizar_diagrama(bloco["codigo"], str(caminho)):
            raise RuntimeError(f"Não foi possível renderizar o diagrama {indice}.")
        bloco["caminho"] = str(caminho)
        bloco.setdefault("legenda", f"Diagrama BPMN {indice}" if bloco["tipo"] == "diagrama_bpmn" else f"Diagrama {indice}")


def argumentos():
    parser = argparse.ArgumentParser(description="Gerador de Documentação Técnica")
    parser.add_argument("--input", help="Arquivo de conteúdo JSON ou Markdown")
    parser.add_argument("--projeto", help="Nome do projeto (padrão: nome do arquivo de entrada)")
    parser.add_argument("--descricao", default="", help="Descrição para a capa")
    parser.add_argument("--organizacao", default="", help="Organização exibida na capa")
    parser.add_argument("--tipo-documento", default="Documentação Técnica", help="Tipo exibido na capa")
    parser.add_argument("--cidade", default="São Paulo", help="Cidade exibida na capa ABNT")
    parser.add_argument("--autor", default="Equipe de Desenvolvimento")
    parser.add_argument("--versao", default="1.0.0")
    parser.add_argument("--classificacao", default="Uso interno", help="Classificação exibida na capa")
    parser.add_argument("--output", default="output", help="Pasta raiz de saída")
    parser.add_argument("--formato", choices=("ambos", "pdf", "docx"), default="ambos")
    parser.add_argument("--sobrescrever", action="store_true", help="Sobrescreve arquivos existentes sem confirmação")
    return parser.parse_args()


def main():
    args = argumentos()
    console.print(Panel.fit("[bold cyan]Gerador de Documentação Técnica — Word + PDF[/bold cyan]", border_style="cyan"))
    try:
        if args.input:
            entrada = Path(args.input).resolve()
            blocos = carregar_entrada(entrada)
            nome = args.projeto or entrada.stem.replace("-", " ").replace("_", " ").title()
            metadados = {"nome_projeto": nome, "descricao": args.descricao, "organizacao": args.organizacao,
                         "tipo_documento": args.tipo_documento, "cidade": args.cidade, "autor": args.autor,
                         "versao": args.versao, "classificacao": args.classificacao,
                         "data_criacao": date.today().strftime("%d/%m/%Y")}
        else:
            metadados = coletar_metadados()
            entrada = Path(Prompt.ask("[yellow]Arquivo JSON ou Markdown[/yellow]")).resolve()
            blocos = carregar_entrada(entrada)
    except (OSError, ValueError, ConteudoInvalido) as erro:
        console.print(f"[red][ERRO] Entrada inválida: {erro}[/red]")
        return 2

    destino = Path(args.output) / slugificar(metadados["nome_projeto"])
    arquivos = [destino / f"{slugificar(metadados['nome_projeto'])}-documentacao.{ext}" for ext in ("docx", "pdf")]
    if any(arquivo.exists() for arquivo in arquivos) and not args.sobrescrever:
        if not Confirm.ask(f"[yellow]Há arquivos em '{destino}'. Sobrescrever?[/yellow]", default=False):
            console.print("[yellow][CANCELADO] Operação cancelada.[/yellow]")
            return 0
    destino.mkdir(parents=True, exist_ok=True)
    try:
        processar_diagramas(blocos, destino / "assets")
        if args.formato in {"ambos", "docx"}:
            gerar_docx(metadados, blocos, str(arquivos[0])); console.print(f"[green][OK] Word criado:[/green] {arquivos[0]}")
        if args.formato in {"ambos", "pdf"}:
            gerar_pdf(metadados, blocos, str(arquivos[1])); console.print(f"[green][OK] PDF criado:[/green] {arquivos[1]}")
    except Exception as erro:
        console.print(f"[red][ERRO] Falha ao gerar a documentação: {erro}[/red]")
        return 1
    console.print(f"[bold green][OK] Documentação criada em: {destino}[/bold green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
