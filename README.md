
# Gerador de Documentações

Aplicação em Python para geração automatizada e padronizada de documentações técnicas em **Word (`.docx`) e PDF**, a partir de arquivos estruturados em **JSON ou Markdown**.

O projeto foi desenvolvido com o objetivo de reduzir o trabalho manual na criação de documentos técnicos, permitindo transformar conteúdos estruturados em arquivos prontos para distribuição.

---

## Sobre o projeto

O **Gerador de Documentações** recebe um arquivo contendo o conteúdo da documentação, realiza validações e normalizações e gera automaticamente documentos em Word e PDF.

A aplicação possui suporte a diferentes tipos de conteúdo, como títulos, textos, listas, tabelas, imagens, links, blocos de código, bibliografia e diagramas.

Também é possível utilizar o sistema por meio de uma **interface de linha de comando (CLI)**, definindo informações como nome do projeto, autor, organização, versão e formato de saída.

---

## Funcionalidades

- Geração de documentos em **DOCX**
- Geração de documentos em **PDF**
- Entrada através de arquivos **JSON**
- Entrada através de arquivos **Markdown**
- Geração simultânea de PDF e Word
- Organização automática dos arquivos de saída
- Validação da estrutura dos conteúdos
- Normalização dos blocos de documentação
- Suporte a:
  - títulos e subtítulos
  - textos
  - listas
  - tabelas
  - imagens
  - links
  - blocos de código
  - callouts
  - bibliografia
  - diagramas Mermaid
  - diagramas BPMN
- Geração automática de sumário
- Tratamento de referências bibliográficas
- Interface CLI interativa
- Configuração de metadados da documentação
- Proteção contra sobrescrita acidental de arquivos
- Testes automatizados para validação das principais regras

---

## Tecnologias

### Linguagem

- Python

### Principais bibliotecas

- `python-docx` — geração de documentos Word
- `ReportLab` — geração de arquivos PDF
- `Pillow` — processamento de imagens
- `Rich` — interface de terminal
- `Requests` — requisições HTTP

---

## Estrutura do projeto

```text
gerador-de-documentacoes/
│
├── core/
│   ├── config.py
│   ├── conteudo.py
│   ├── diagramas.py
│   ├── estrutura.py
│   ├── imagens.py
│   ├── markdown_parser.py
│   ├── pdf.py
│   └── word.py
│
├── tests/
│   ├── fixture_documentacao.json
│   └── test_conteudo.py
│
├── exemplo-conteudo.json
├── GUIA_DE_USO.md
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Principais módulos

**`main.py`**  
Responsável pela interface de linha de comando e pela orquestração do processo de geração.

**`core/conteudo.py`**  
Realiza validação e normalização dos conteúdos recebidos.

**`core/markdown_parser.py`**  
Converte conteúdos Markdown para a estrutura interna utilizada pela aplicação.

**`core/pdf.py`**  
Responsável pela geração dos documentos PDF.

**`core/word.py`**  
Responsável pela geração dos documentos Word.

**`core/diagramas.py`**  
Responsável pelo processamento e renderização dos diagramas.

**`core/estrutura.py`**  
Organiza os conteúdos, sumário e referências da documentação.

---

## Pré-requisitos

Antes de executar o projeto, certifique-se de possuir:

- Python instalado
- Git instalado
- `pip` disponível no ambiente

---

## Instalação

Clone o repositório:

```bash
git clone https://github.com/LucasCieczinski/gerador-de-documentacoes.git
```

Acesse a pasta:

```bash
cd gerador-de-documentacoes
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Como utilizar

A aplicação pode receber arquivos **JSON** ou **Markdown**.

### Execução básica

```bash
python main.py --input exemplo-conteudo.json
```

Por padrão, serão gerados:

```text
output/
└── nome-do-projeto/
    ├── nome-do-projeto-documentacao.docx
    └── nome-do-projeto-documentacao.pdf
```

---

## Utilizando Markdown

Também é possível utilizar um arquivo Markdown como entrada:

```bash
python main.py --input documentacao.md
```

O sistema converte o Markdown para a estrutura interna de documentação antes da geração dos arquivos.

---

## Escolhendo o formato de saída

Gerar somente PDF:

```bash
python main.py --input exemplo-conteudo.json --formato pdf
```

Gerar somente Word:

```bash
python main.py --input exemplo-conteudo.json --formato docx
```

Gerar ambos:

```bash
python main.py --input exemplo-conteudo.json --formato ambos
```

---

## Personalizando a documentação

É possível configurar diversos metadados diretamente pela CLI:

```bash
python main.py \
  --input exemplo-conteudo.json \
  --projeto "Meu Projeto" \
  --descricao "Documentação técnica da aplicação" \
  --organizacao "Minha Organização" \
  --autor "Nome do Autor" \
  --versao "1.0.0"
```

Outros parâmetros disponíveis incluem:

```text
--tipo-documento
--cidade
--classificacao
--output
--formato
--sobrescrever
```

Para visualizar todas as opções:

```bash
python main.py --help
```

---

## Exemplo de entrada JSON

A estrutura mínima esperada utiliza uma lista de seções:

```json
{
  "secoes": [
    {
      "tipo": "titulo",
      "texto": "Visão Geral"
    },
    {
      "tipo": "texto",
      "texto": "Descrição geral da aplicação."
    },
    {
      "tipo": "lista",
      "itens": [
        "Java",
        "Spring Boot",
        "PostgreSQL"
      ]
    }
  ]
}
```

A aplicação valida os tipos e os campos obrigatórios antes de gerar os documentos.

---

## Tipos de conteúdo suportados

```text
titulo
subtitulo
secao_nivel_3
texto
codigo
imagem
diagrama_mermaid
diagrama_bpmn
link
lista
tabela
callout
bibliografia
```

---

## Testes

O projeto possui testes automatizados utilizando `unittest`.

Para executar:

```bash
python -m unittest discover tests
```

Os testes atualmente validam cenários relacionados a:

- conversão de Markdown
- níveis de títulos
- tabelas
- validação de conteúdo
- geração de sumário
- referências bibliográficas
- diagramas

---

## Exemplo de fluxo

```text
JSON / Markdown
       │
       ▼
Leitura da entrada
       │
       ▼
Validação e normalização
       │
       ▼
Processamento da estrutura
       │
       ├── Imagens
       ├── Tabelas
       ├── Diagramas
       ├── Referências
       └── Sumário
       │
       ▼
Geração dos documentos
       │
       ├── DOCX
       └── PDF
```

---

## Objetivo do projeto

Este projeto foi desenvolvido como iniciativa pessoal para praticar e aplicar conceitos relacionados a:

- Python
- automação de processos
- manipulação de arquivos
- geração programática de documentos
- organização modular de aplicações
- validação de dados
- desenvolvimento de ferramentas CLI
- testes automatizados

---

## Autor

**Lucas Cieczinski Peres**

Desenvolvedor Backend com foco em Java, Spring Boot e PostgreSQL, com interesse em automação, arquitetura de software e desenvolvimento de ferramentas.

[LinkedIn](https://www.linkedin.com/in/lucas-cieczinski-peres-ab226137b/)
