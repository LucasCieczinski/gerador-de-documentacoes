# core/config.py
from reportlab.lib import colors

# Paleta de Cores Moderna / Corporativa (Azul Profundo & Neutros)
PALETA = {
    "primaria": colors.HexColor("#0F172A"),      # Azul escuro elegante (Slate 900)
    "secundaria": colors.HexColor("#2563EB"),    # Azul vibrante (Blue 600)
    "fundo": colors.HexColor("#F8FAFC"),         # Cinza muito claro/gelo (Slate 50)
    "texto": colors.HexColor("#334155"),         # Cinza escuro para leitura confortável (Slate 700)
    "borda": colors.HexColor("#E2E8F0"),         # Cinza suave para bordas e grids (Slate 200)
    "destaque": colors.HexColor("#EFF6FF")       # Azul bem claro para fundos de destaque
}

CONFIG_PDF = {
    "font_name": "Helvetica",
    "font_name_bold": "Helvetica-Bold",
    "logo_path": "assets/logo.png"
}