import unittest

from core.conteudo import ConteudoInvalido, normalizar_blocos
from core.markdown_parser import converter_markdown_para_json
from core.estrutura import preparar_conteudo


class ConteudoTest(unittest.TestCase):
    def test_markdown_preserva_tres_niveis_e_blocos(self):
        blocos = converter_markdown_para_json(
            "# Principal\n\n## Secundário\n\n### Terciário\n\n> Nota\n\n```python\nprint('ok')\n```"
        )["secoes"]
        self.assertEqual([bloco["tipo"] for bloco in blocos], ["titulo", "subtitulo", "secao_nivel_3", "callout", "codigo"])

    def test_normaliza_colunas_de_tabelas_antigas(self):
        blocos = normalizar_blocos(
            [{"tipo": "tabela", "colunas": ["A", "B"], "linhas": [[1, "dois"]]}], "."
        )
        self.assertEqual(blocos[0]["cabecalhos"], ["A", "B"])
        self.assertEqual(blocos[0]["linhas"], [["1", "dois"]])

    def test_rejeita_tabela_com_linha_incompleta(self):
        with self.assertRaises(ConteudoInvalido):
            normalizar_blocos([{"tipo": "tabela", "cabecalhos": ["A", "B"], "linhas": [["A"]]}], ".")

    def test_sumario_e_bibliografia_sao_derivados_do_conteudo(self):
        conteudo, sumario, referencias = preparar_conteudo([
            {"tipo": "titulo", "texto": "Visão geral"},
            {"tipo": "subtitulo", "texto": "Contexto"},
            {"tipo": "link", "texto": "Fonte oficial", "url": "https://exemplo.com"},
            {"tipo": "bibliografia", "itens": [{"titulo": "Livro", "autor": "Autor"}]},
        ])
        self.assertEqual([(item["numero"], item["texto"]) for item in sumario], [("1", "Visão geral"), ("1.1", "Contexto"), ("2", "Referências")])
        self.assertEqual([item["titulo"] for item in referencias], ["Fonte oficial", "Livro"])
        self.assertNotIn("bibliografia", [bloco["tipo"] for bloco in conteudo])

    def test_diagrama_bpmn_recebe_fonte_padrao(self):
        blocos = normalizar_blocos([{"tipo": "diagrama_bpmn", "codigo": "flowchart LR\nA-->B"}], ".")
        self.assertEqual(blocos[0]["fonte"], "Elaborado pelo autor.")


if __name__ == "__main__":
    unittest.main()
