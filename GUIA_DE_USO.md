# Gerador de Documentação Técnica

Crie uma documentação padronizada a partir de Markdown ou JSON e gere PDF, Word ou ambos.

```powershell
py main.py --input .\termos.md --projeto "Tela de Termos" --autor "Minha Equipe" --formato ambos --sobrescrever
```

O nome do projeto é opcional: se omitido, ele é derivado do nome do arquivo de entrada. Os arquivos são criados em `output/<nome-do-projeto>/`; use `--output <pasta>` para mudar a raiz de saída.

## Blocos JSON suportados

- `titulo`, `subtitulo` e `secao_nivel_3`: exigem `texto`.
- `texto`, `codigo` e `callout`: exigem `texto`.
- `lista`: exige `itens`, uma lista de textos.
- `imagem`: exige `caminho`; caminhos relativos são resolvidos a partir do JSON/Markdown. Use `fonte` para a origem; se omitida, o documento usa `Elaborado pelo autor.`.
- `diagrama_mermaid`: exige `codigo`; o PNG é criado automaticamente em `assets/`.
- `tabela`: exige `cabecalhos` e `linhas`. O campo legado `colunas` continua aceito.
- `link`: exige `texto` e URL `http` ou `https`.
- `bibliografia`: exige `itens`; cada item possui `titulo` e pode incluir `autor`, `url` e `data_acesso`.

Markdown reconhece títulos até `###`, listas, imagens, links isolados, citações (`>`) e blocos de código. Blocos identificados como `mermaid` são convertidos em diagramas.

Para adicionar a fonte de uma imagem Markdown, insira a linha seguinte: `Fonte: Nome da organização ou URL`. No JSON, use também o tipo `diagrama_bpmn` para fluxos BPMN já descritos em Mermaid; para aderência formal à BPMN, forneça o modelo BPMN validado pela sua ferramenta de modelagem.

Os links e os itens `bibliografia` são consolidados automaticamente em uma seção final de Referências. O sumário também é construído a partir dos títulos reais do conteúdo, incluindo seus três níveis.
