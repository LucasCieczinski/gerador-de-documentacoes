"""Utilitários de imagem compartilhados entre os geradores de PDF e Word."""

from PIL import Image

# Largura útil aproximada de uma página A4 com margens padrão (em polegadas).
# Usada tanto no Word quanto no PDF para as imagens ficarem consistentes nos dois formatos.
LARGURA_UTIL_POL = 6.3


def dimensoes_proporcionais(caminho_imagem, largura_maxima):
    """Retorna (largura, altura) mantendo a proporção original da imagem,
    respeitando a largura máxima informada (na mesma unidade de largura_maxima)."""
    with Image.open(caminho_imagem) as img:
        largura_original, altura_original = img.size

    proporcao = altura_original / largura_original
    largura = largura_maxima
    altura = largura * proporcao
    return largura, altura
