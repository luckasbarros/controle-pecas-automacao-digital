import tempfile
import unittest
from pathlib import Path

from controle_pecas import ArquivoCadastro, Cadastro, Peca


class ControlePecasTestes(unittest.TestCase):
    def peca(self, identificador, peso="100", cor="azul", comprimento="15"):
        return Peca.criar(identificador, peso, cor, comprimento)

    def test_limites_sao_inclusivos_e_aceita_virgula(self):
        self.assertTrue(self.peca("A", "95", "Azul", "10").aprovada)
        self.assertTrue(self.peca("B", "105", "verde", "20").aprovada)
        self.assertTrue(self.peca("C", "100,5", " AZUL ", "15,5").aprovada)

    def test_relatorio_registra_todos_os_motivos(self):
        cadastro = Cadastro([self.peca("R1", "94", "vermelho", "21")])
        relatorio = cadastro.relatorio()
        self.assertEqual(relatorio["reprovadas"], 1)
        self.assertEqual(len(relatorio["pecas_reprovadas"][0]["motivos"]), 3)
        self.assertEqual(sum(relatorio["motivos"].values()), 3)

    def test_caixas_fecham_ao_atingir_dez_e_remocao_reorganiza(self):
        cadastro = Cadastro([self.peca(f"P{i}") for i in range(1, 12)])
        self.assertEqual(len(cadastro.caixas_fechadas), 1)
        self.assertEqual(len(cadastro.caixa_aberta), 1)
        self.assertEqual(cadastro.caixas_utilizadas, 2)
        cadastro.remover("P1")
        self.assertEqual(len(cadastro.caixas_fechadas), 1)
        self.assertEqual(len(cadastro.caixa_aberta), 0)
        self.assertEqual(cadastro.caixas_fechadas[0][0].id, "P2")

    def test_id_unico_e_campos_validos(self):
        cadastro = Cadastro([self.peca("ABC")])
        with self.assertRaises(ValueError):
            cadastro.adicionar(self.peca("abc"))
        for peso in ("0", "-1", "nan", "abc"):
            with self.assertRaises(ValueError):
                self.peca("X", peso=peso)

    def test_persistencia_preserva_dados(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = ArquivoCadastro(Path(pasta) / "dados.json")
            cadastro = Cadastro([self.peca("A", "100,5", "verde", "15")])
            arquivo.salvar(cadastro)
            recuperado = arquivo.carregar()
            self.assertEqual(recuperado.pecas, cadastro.pecas)
            self.assertEqual(recuperado.relatorio()["aprovadas"], 1)

    def test_lotes_repetidos_somam_por_nome_mas_mantem_ids_individuais(self):
        cadastro = Cadastro()
        primeiro = cadastro.adicionar_lote("Parafuso M4", "100", "azul", "15", "3")
        segundo = cadastro.adicionar_lote("Parafuso M4", "100", "azul", "15", "2")
        self.assertEqual([peca.id for peca in primeiro + segundo],
                         [f"P{i:06d}" for i in range(1, 6)])
        self.assertEqual(cadastro.relatorio()["por_nome"][0]["total"], 5)
        cadastro.remover("P000002")
        self.assertEqual(cadastro.relatorio()["por_nome"][0]["total"], 4)
        self.assertIn("P000003", [peca.id for peca in cadastro.pecas])
        self.assertEqual(cadastro.adicionar_lote("Parafuso M4", "100", "azul", "15", 1)[0].id,
                         "P000006")

    def test_reprovacao_por_cor_e_multiplos_motivos_em_lote(self):
        cadastro = Cadastro()
        cadastro.adicionar_lote("Arruela", "94", "vermelho", "21", "2")
        relatorio = cadastro.relatorio()
        self.assertEqual(relatorio["reprovadas"], 2)
        self.assertEqual(len(relatorio["pecas_reprovadas"][0]["motivos"]), 3)
        self.assertEqual(relatorio["motivos"]["cor diferente de azul ou verde"], 2)

    def test_arquivo_antigo_sem_nome_continua_legivel(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            caminho.write_text('{"versao": 1, "pecas": [{"id": "A", "peso": "100", '
                               '"cor": "azul", "comprimento": "15"}]}', encoding="utf-8")
            cadastro = ArquivoCadastro(caminho).carregar()
            self.assertEqual(cadastro.pecas[0].nome, "A")

    def test_proximo_id_persiste_mesmo_apos_excluir_ultimo(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = ArquivoCadastro(Path(pasta) / "dados.json")
            cadastro = Cadastro()
            cadastro.adicionar_lote("Peça", "100", "azul", "15", 2)
            cadastro.remover("P000002")
            arquivo.salvar(cadastro)
            recuperado = arquivo.carregar()
            nova = recuperado.adicionar_lote("Peça", "100", "azul", "15", 1)[0]
            self.assertEqual(nova.id, "P000003")


if __name__ == "__main__":
    unittest.main()
