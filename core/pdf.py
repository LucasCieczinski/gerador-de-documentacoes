"""Gerador PDF A4 para todos os blocos normalizados de conteúdo."""

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.imagens import dimensoes_proporcionais
from core.estrutura import preparar_conteudo


def gerar_pdf(metadados, secoes, caminho_saida):
    doc = SimpleDocTemplate(caminho_saida, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2.3 * cm, bottomMargin=2 * cm)
    estilos = _estilos()
    conteudo, sumario, referencias = preparar_conteudo(secoes)
    story = _capa(metadados, estilos)
    if sumario:
        story.extend(_sumario(sumario, estilos))
    for bloco in conteudo:
        story.extend(_renderizar_bloco(bloco, estilos, doc.width))
    if referencias:
        story.extend(_bibliografia(referencias, estilos))
    titulo = metadados.get("nome_projeto", "Documentação")
    doc.build(story, onFirstPage=lambda c, d: _rodape(c, d, titulo), onLaterPages=lambda c, d: _cabecalho_rodape(c, d, titulo))


def _estilos():
    base = getSampleStyleSheet()["Normal"]
    return {
        "kicker": ParagraphStyle("Kicker", parent=base, fontName="Helvetica-Bold", fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#2563EB"), spaceAfter=10),
        "capa": ParagraphStyle("Capa", parent=base, fontName="Helvetica-Bold", fontSize=28, leading=34, alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"), spaceAfter=14),
        "subcapa": ParagraphStyle("Subcapa", parent=base, fontSize=12, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=26),
        "h1": ParagraphStyle("H1", parent=base, fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#0F172A"), spaceBefore=15, spaceAfter=7, keepWithNext=True),
        "h2": ParagraphStyle("H2", parent=base, fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor("#2563EB"), spaceBefore=11, spaceAfter=5, keepWithNext=True),
        "h3": ParagraphStyle("H3", parent=base, fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#334155"), spaceBefore=9, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base, fontSize=10, leading=14, textColor=colors.HexColor("#334155"), alignment=TA_JUSTIFY, spaceAfter=7),
        "code": ParagraphStyle("Code", parent=base, fontName="Courier", fontSize=8, leading=10, backColor=colors.HexColor("#F1F5F9"), borderPadding=6, spaceAfter=9),
        "caption": ParagraphStyle("Caption", parent=base, fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#64748B"), spaceAfter=12),
        "figure_title": ParagraphStyle("FigureTitle", parent=base, fontSize=10, leading=13, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4),
        "figure_source": ParagraphStyle("FigureSource", parent=base, fontSize=9, leading=11, textColor=colors.HexColor("#334155"), spaceBefore=3, spaceAfter=11),
    }


def _capa(metadados, estilos):
    instituicao = ParagraphStyle("Instituicao", parent=estilos["body"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#0F172A"), spaceAfter=58)
    autor = ParagraphStyle("Autor", parent=estilos["body"], alignment=TA_CENTER, fontSize=12, textColor=colors.HexColor("#334155"), spaceAfter=72)
    titulo = ParagraphStyle("TituloABNT", parent=estilos["capa"], fontSize=16, leading=20, spaceAfter=10)
    local = ParagraphStyle("Local", parent=estilos["body"], alignment=TA_CENTER, fontSize=11, spaceAfter=2)
    ano = ParagraphStyle("Ano", parent=estilos["body"], alignment=TA_CENTER, fontSize=11)
    ano_texto = metadados.get("data_criacao", "").split("/")[-1]
    return [Spacer(1, 2.2 * cm), Paragraph(_e(metadados.get("organizacao", "INSTITUIÇÃO NÃO INFORMADA").upper()), instituicao), Paragraph(_e(metadados.get("autor", "AUTOR NÃO INFORMADO").upper()), autor), Paragraph(_e(metadados.get("nome_projeto", "Documentação").upper()), titulo), Paragraph(_e(metadados.get("tipo_documento", "Documentação Técnica")), estilos["subcapa"]), Paragraph(_e(metadados.get("descricao", "")), estilos["subcapa"]), Spacer(1, 4.1 * cm), Paragraph(_e(metadados.get("cidade", "São Paulo")), local), Paragraph(_e(ano_texto), ano), PageBreak()]


def _sumario(itens, estilos):
    story = [Paragraph("Sumário", estilos["h1"])]
    for item in itens:
        estilo = ParagraphStyle(f"Sumario{item['nivel']}", parent=estilos["body"], leftIndent=(item["nivel"] - 1) * 14, spaceAfter=4, textColor=colors.HexColor("#0F172A") if item["nivel"] == 1 else colors.HexColor("#334155"))
        rotulo = f"{item['numero']} {_e(item['texto'])}"
        texto = f"<b>{rotulo}</b>" if item["nivel"] == 1 else rotulo
        story.append(Paragraph(texto, estilo))
    return [*story, PageBreak()]


def _bibliografia(referencias, estilos):
    story = [Paragraph("Referências", estilos["h1"])]
    for indice, referencia in enumerate(referencias, start=1):
        partes = [f"<b>{indice}.</b> {_e(referencia['titulo'])}"]
        if referencia.get("autor"): partes.append(_e(referencia["autor"]))
        if referencia.get("url"): partes.append(f"Disponível em: {_e(referencia['url'])}")
        if referencia.get("data_acesso"): partes.append(f"Acesso em: {_e(referencia['data_acesso'])}")
        story.append(Paragraph(". ".join(partes), estilos["body"]))
    return story


def _renderizar_bloco(bloco, estilos, largura_util):
    tipo = bloco["tipo"]
    if tipo in {"titulo", "subtitulo", "secao_nivel_3"}:
        return [Paragraph(_e(bloco["texto"]), estilos[{"titulo": "h1", "subtitulo": "h2", "secao_nivel_3": "h3"}[tipo]])]
    if tipo == "texto": return [Paragraph(_e(bloco["texto"]), estilos["body"])]
    if tipo == "codigo": return [Paragraph(_e(bloco["texto"]).replace("\n", "<br/>"), estilos["code"])]
    if tipo == "lista": return [Paragraph(f"• {_e(item)}", ParagraphStyle("Item", parent=estilos["body"], leftIndent=14, firstLineIndent=-9, spaceAfter=4)) for item in bloco["itens"]]
    if tipo in {"imagem", "diagrama_mermaid", "diagrama_bpmn"}: return _imagem(bloco, estilos, largura_util)
    if tipo == "link": return [Paragraph(f"<b>{_e(bloco['texto'])}</b>: {_e(bloco['url'])}", estilos["body"])]
    if tipo == "callout":
        tabela = Table([[Paragraph(_e(bloco["texto"]), estilos["body"])]], colWidths=[largura_util])
        tabela.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")), ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#93C5FD")), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
        return [tabela, Spacer(1, 8)]
    if tipo == "tabela":
        estilo_cabecalho = ParagraphStyle("TableHeader", parent=estilos["body"], textColor=colors.white, alignment=TA_CENTER)
        dados = [[Paragraph(f"<b>{_e(c)}</b>", estilo_cabecalho) for c in bloco["cabecalhos"]]] + [[Paragraph(_e(c), estilos["body"]) for c in linha] for linha in bloco["linhas"]]
        tabela = Table(dados, colWidths=[largura_util / len(bloco["cabecalhos"])] * len(bloco["cabecalhos"]), repeatRows=1)
        tabela.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#CBD5E1")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return [tabela, Spacer(1, 10)]
    return []


def _imagem(bloco, estilos, largura_util):
    caminho = bloco.get("caminho", "")
    if not Path(caminho).is_file(): return [Paragraph(f"[Imagem não encontrada: {_e(caminho)}]", estilos["body"])]
    largura, altura = dimensoes_proporcionais(caminho, largura_util * .86)
    if altura > 390:
        proporcao = 390 / altura; largura, altura = largura * proporcao, 390
    imagem = Image(caminho, width=largura, height=altura); imagem.hAlign = "CENTER"
    numero = bloco.get("_numero_figura", "")
    descricao = bloco.get("legenda") or ("Diagrama BPMN" if bloco["tipo"] == "diagrama_bpmn" else "Imagem")
    fonte = bloco.get("fonte", "Elaborado pelo autor.")
    return [KeepTogether([Paragraph(f"Figura {numero} - {_e(descricao)}", estilos["figure_title"]), imagem, Paragraph(f"Fonte: {_e(fonte)}", estilos["figure_source"])])]


def _cabecalho_rodape(canvas, doc, titulo):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(doc.leftMargin, A4[1] - 1.25 * cm, titulo); canvas.line(doc.leftMargin, A4[1] - 1.45 * cm, A4[0] - doc.rightMargin, A4[1] - 1.45 * cm)
    _rodape(canvas, doc, titulo); canvas.restoreState()


def _rodape(canvas, doc, titulo):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#64748B")); canvas.drawRightString(A4[0] - doc.rightMargin, 1.1 * cm, f"Página {doc.page}"); canvas.restoreState()


def _e(valor):
    return escape(str(valor))
