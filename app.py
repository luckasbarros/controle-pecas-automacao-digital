"""Interface gráfica do controle de produção e qualidade de peças."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from controle_pecas import ArquivoCadastro, Cadastro, Peca


FUNDO = "#f3f6fb"
BRANCO = "#ffffff"
AZUL = "#183153"
AZUL_CLARO = "#e8f0fb"
TEXTO = "#213047"
MUTED = "#65758b"
VERDE = "#18794e"
VERMELHO = "#b42333"


def numero(valor) -> str:
    return format(valor, "f").rstrip("0").rstrip(".") if "." in format(valor, "f") else str(valor)


class Aplicativo(tk.Tk):
    def __init__(self, cadastro: Cadastro, arquivo: ArquivoCadastro):
        super().__init__()
        self.cadastro = cadastro
        self.arquivo = arquivo
        self.title("Controle de Peças | Qualidade e Armazenamento")
        self.geometry("1100x720")
        self.minsize(850, 570)
        self.configure(bg=FUNDO)
        self._configurar_estilos()
        self._montar_estrutura()
        self.mostrar_inicio()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=FUNDO)
        estilo.configure("Card.TFrame", background=BRANCO)
        estilo.configure("TLabel", background=FUNDO, foreground=TEXTO, font=("Segoe UI", 10))
        estilo.configure("Card.TLabel", background=BRANCO, foreground=TEXTO, font=("Segoe UI", 10))
        estilo.configure("TEntry", padding=8, font=("Segoe UI", 10))
        estilo.configure("TButton", padding=(14, 9), font=("Segoe UI Semibold", 10))
        estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=32, background=BRANCO,
                         fieldbackground=BRANCO, foreground=TEXTO, borderwidth=0)
        estilo.configure("Treeview.Heading", font=("Segoe UI Semibold", 10), padding=8,
                         background=AZUL_CLARO, foreground=AZUL)
        estilo.map("Treeview", background=[("selected", "#d7e7fb")],
                   foreground=[("selected", TEXTO)])

    def _montar_estrutura(self) -> None:
        self.sidebar = tk.Frame(self, bg=AZUL, width=235)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="CONTROLE DE PEÇAS", bg=AZUL, fg=BRANCO,
                 font=("Segoe UI Semibold", 15), wraplength=200,
                 justify="left").pack(anchor="w", padx=20, pady=(28, 5))
        tk.Label(self.sidebar, text="Qualidade e armazenamento", bg=AZUL,
                 fg="#b9cce5", font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(0, 25))

        itens = [
            ("Visão geral", self.mostrar_inicio),
            ("1  Cadastrar nova peça", self.mostrar_cadastro),
            ("2  Listar peças", self.mostrar_listagem),
            ("3  Remover peça", self.mostrar_remocao),
            ("4  Caixas fechadas", self.mostrar_caixas),
            ("5  Relatório final", self.mostrar_relatorio),
        ]
        for rotulo, comando in itens:
            tk.Button(self.sidebar, text=rotulo, command=comando, anchor="w",
                      bg=AZUL, fg=BRANCO, activebackground="#28496e",
                      activeforeground=BRANCO, relief="flat", bd=0,
                      font=("Segoe UI", 10), padx=20, pady=12,
                      cursor="hand2").pack(fill="x")
        tk.Button(self.sidebar, text="Sair", command=self.destroy, anchor="w",
                  bg=AZUL, fg="#b9cce5", activebackground="#28496e",
                  activeforeground=BRANCO, relief="flat", bd=0,
                  font=("Segoe UI", 10), padx=20, pady=12,
                  cursor="hand2").pack(side="bottom", fill="x", pady=15)

        self.conteudo = tk.Frame(self, bg=FUNDO)
        self.conteudo.pack(side="left", fill="both", expand=True, padx=32, pady=26)

    def _limpar(self, titulo: str, subtitulo: str = "") -> tk.Frame:
        for widget in self.conteudo.winfo_children():
            widget.destroy()
        tk.Label(self.conteudo, text=titulo, bg=FUNDO, fg=AZUL,
                 font=("Segoe UI Semibold", 22)).pack(anchor="w")
        if subtitulo:
            tk.Label(self.conteudo, text=subtitulo, bg=FUNDO, fg=MUTED,
                     font=("Segoe UI", 10), wraplength=750,
                     justify="left").pack(anchor="w", pady=(4, 20))
        else:
            tk.Frame(self.conteudo, bg=FUNDO, height=18).pack()
        return self.conteudo

    def _cartao(self, pai, titulo: str, valor: str, coluna: int) -> None:
        quadro = tk.Frame(pai, bg=BRANCO, highlightbackground="#dce4ef", highlightthickness=1)
        quadro.grid(row=0, column=coluna, sticky="nsew", padx=(0, 12))
        tk.Label(quadro, text=titulo, bg=BRANCO, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(16, 5))
        tk.Label(quadro, text=valor, bg=BRANCO, fg=AZUL,
                 font=("Segoe UI Semibold", 25)).pack(anchor="w", padx=18, pady=(0, 17))

    def _resumo(self, pai) -> None:
        dados = self.cadastro.relatorio()
        linha = tk.Frame(pai, bg=FUNDO)
        linha.pack(fill="x", pady=(0, 22))
        for coluna in range(4):
            linha.grid_columnconfigure(coluna, weight=1)
        self._cartao(linha, "Peças cadastradas", str(dados["total"]), 0)
        self._cartao(linha, "Aprovadas", str(dados["aprovadas"]), 1)
        self._cartao(linha, "Reprovadas", str(dados["reprovadas"]), 2)
        self._cartao(linha, "Caixas utilizadas", str(dados["caixas_utilizadas"]), 3)

    def _botao(self, pai, texto: str, comando, destaque: bool = False) -> tk.Button:
        botao = tk.Button(pai, text=texto, command=comando,
                          bg=AZUL if destaque else AZUL_CLARO,
                          fg=BRANCO if destaque else AZUL,
                          activebackground="#28496e" if destaque else "#d7e7fb",
                          activeforeground=BRANCO if destaque else AZUL,
                          relief="flat", bd=0, font=("Segoe UI Semibold", 10),
                          padx=18, pady=10, cursor="hand2")
        return botao

    def mostrar_inicio(self) -> None:
        pai = self._limpar("Visão geral", "Acompanhe a produção e acesse as funções pelo menu lateral.")
        self._resumo(pai)
        quadro = tk.Frame(pai, bg=BRANCO, padx=24, pady=24,
                          highlightbackground="#dce4ef", highlightthickness=1)
        quadro.pack(fill="x")
        tk.Label(quadro, text="Critérios de aprovação", bg=BRANCO, fg=AZUL,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w")
        for regra in ("Peso: de 95 g a 105 g", "Cor: azul ou verde",
                      "Comprimento: de 10 cm a 20 cm", "Caixa: máximo de 10 peças aprovadas"):
            tk.Label(quadro, text="•  " + regra, bg=BRANCO, fg=TEXTO,
                     font=("Segoe UI", 11)).pack(anchor="w", pady=(9, 0))
        self._botao(pai, "Cadastrar peça", self.mostrar_cadastro, True).pack(anchor="w", pady=22)

    def mostrar_cadastro(self) -> None:
        pai = self._limpar("Cadastrar novas peças", "Informe nome e quantidade. O ID de cada unidade é gerado automaticamente. Vírgula ou ponto são aceitos nos números.")
        quadro = tk.Frame(pai, bg=BRANCO, padx=26, pady=22,
                          highlightbackground="#dce4ef", highlightthickness=1)
        quadro.pack(fill="x")
        entradas = {}
        campos = [("Nome da peça", "nome"), ("Quantidade", "quantidade"), ("Peso (g)", "peso"),
                  ("Cor", "cor"), ("Comprimento (cm)", "comprimento")]
        for linha, (rotulo, chave) in enumerate(campos):
            tk.Label(quadro, text=rotulo, bg=BRANCO, fg=TEXTO,
                     font=("Segoe UI Semibold", 10)).grid(row=linha, column=0, sticky="w", pady=11)
            if chave == "cor":
                entrada = ttk.Combobox(quadro, width=36, state="readonly",
                                       values=("azul", "verde", "vermelho", "amarelo",
                                               "preto", "branco", "outra"))
            else:
                entrada = ttk.Entry(quadro, width=38)
            entrada.grid(row=linha, column=1, sticky="ew", padx=(20, 0), pady=8)
            entradas[chave] = entrada
        quadro.grid_columnconfigure(1, weight=1)
        entradas["nome"].focus_set()

        def cadastrar() -> None:
            try:
                valores = {chave: entrada.get() for chave, entrada in entradas.items()}
                if not valores["cor"]:
                    raise ValueError("Selecione a cor da peça.")
                novo = Cadastro(self.cadastro.pecas, self.cadastro.proximo_id)
                fechadas_antes = len(novo.caixas_fechadas)
                criadas = novo.adicionar_lote(**valores)
                self.arquivo.salvar(novo)
            except (ValueError, OSError) as erro:
                messagebox.showerror("Cadastro não realizado", str(erro), parent=self)
                return
            self.cadastro = novo
            quantidade = len(criadas)
            if criadas[0].aprovada:
                mensagem = f"{quantidade} peça(s) aprovada(s) e armazenada(s)."
                novas_caixas = len(novo.caixas_fechadas) - fechadas_antes
                if novas_caixas:
                    mensagem += f" {novas_caixas} caixa(s) foi/foram fechada(s)."
            else:
                mensagem = (f"{quantidade} peça(s) reprovada(s): "
                            + "; ".join(criadas[0].motivos_reprovacao) + ".")
            mensagem += f"\nIDs: {criadas[0].id}"
            if quantidade > 1:
                mensagem += f" até {criadas[-1].id}"
            messagebox.showinfo("Cadastro concluído", mensagem, parent=self)
            self.mostrar_cadastro()

        self._botao(pai, "Cadastrar peça", cadastrar, True).pack(anchor="w", pady=20)

    def _tabela_pecas(self, pai, pecas: list[Peca]) -> ttk.Treeview:
        area = tk.Frame(pai, bg=FUNDO)
        area.pack(fill="both", expand=True)
        colunas = ("id", "nome", "peso", "cor", "comprimento", "situacao", "motivos")
        tabela = ttk.Treeview(area, columns=colunas, show="headings", selectmode="browse")
        cabecalhos = {"id": "ID", "nome": "Nome", "peso": "Peso (g)", "cor": "Cor",
                      "comprimento": "Compr. (cm)", "situacao": "Situação",
                      "motivos": "Motivo da reprovação"}
        larguras = {"id": 120, "nome": 150, "peso": 90, "cor": 95, "comprimento": 110,
                    "situacao": 105, "motivos": 340}
        for coluna in colunas:
            tabela.heading(coluna, text=cabecalhos[coluna])
            tabela.column(coluna, width=larguras[coluna], minwidth=80,
                          stretch=coluna == "motivos")
        tabela.tag_configure("aprovada", foreground=VERDE)
        tabela.tag_configure("reprovada", foreground=VERMELHO)
        for peca in pecas:
            tabela.insert("", "end", iid=peca.id,
                          values=(peca.id, peca.nome, numero(peca.peso), peca.cor,
                                  numero(peca.comprimento),
                                  "Aprovada" if peca.aprovada else "Reprovada",
                                  "; ".join(peca.motivos_reprovacao) or "—"),
                          tags=("aprovada" if peca.aprovada else "reprovada",))
        barra_vertical = ttk.Scrollbar(area, orient="vertical", command=tabela.yview)
        barra_horizontal = ttk.Scrollbar(area, orient="horizontal", command=tabela.xview)
        tabela.configure(yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)
        tabela.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(0, weight=1)
        return tabela

    def mostrar_listagem(self) -> None:
        pai = self._limpar("Peças cadastradas", "Consulte, filtre e remova peças. Cada linha representa uma unidade com ID próprio.")
        filtro = tk.StringVar(value="Todas")
        barra = tk.Frame(pai, bg=FUNDO)
        barra.pack(fill="x", pady=(0, 12))
        tk.Label(barra, text="Mostrar:", bg=FUNDO, fg=TEXTO,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        for texto in ("Todas", "Aprovadas", "Reprovadas"):
            ttk.Radiobutton(barra, text=texto, value=texto, variable=filtro,
                            command=self.mostrar_listagem_filtrada).pack(side="left", padx=8)
        self._filtro = filtro
        self._tabela = self._tabela_pecas(pai, self.cadastro.pecas)
        self._botao(pai, "Remover peça selecionada",
                    lambda: self._remover_selecionada(self._tabela), True).pack(anchor="w", pady=(16, 0))

    def mostrar_listagem_filtrada(self) -> None:
        escolha = self._filtro.get()
        pecas = (self.cadastro.pecas if escolha == "Todas" else
                 self.cadastro.aprovadas if escolha == "Aprovadas" else self.cadastro.reprovadas)
        for item in self._tabela.get_children():
            self._tabela.delete(item)
        for peca in pecas:
            self._tabela.insert("", "end", iid=peca.id,
                                values=(peca.id, peca.nome, numero(peca.peso), peca.cor,
                                        numero(peca.comprimento),
                                        "Aprovada" if peca.aprovada else "Reprovada",
                                        "; ".join(peca.motivos_reprovacao) or "—"),
                                tags=("aprovada" if peca.aprovada else "reprovada",))

    def mostrar_remocao(self) -> None:
        self.mostrar_listagem()

    def _remover_selecionada(self, tabela: ttk.Treeview) -> None:
        selecao = tabela.selection()
        if not selecao:
            messagebox.showwarning("Selecione uma peça", "Escolha uma peça na lista.", parent=self)
            return
        identificador = selecao[0]
        if not messagebox.askyesno("Confirmar remoção", f"Remover a peça '{identificador}'? As caixas serão reorganizadas.", parent=self):
            return
        try:
            novo = Cadastro(self.cadastro.pecas, self.cadastro.proximo_id)
            novo.remover(identificador)
            self.arquivo.salvar(novo)
        except (ValueError, OSError) as erro:
            messagebox.showerror("Remoção não realizada", str(erro), parent=self)
            return
        self.cadastro = novo
        self.mostrar_listagem()
        messagebox.showinfo("Peça removida", f"A peça '{identificador}' foi removida.", parent=self)

    def mostrar_caixas(self) -> None:
        pai = self._limpar("Caixas fechadas", "Cada caixa é fechada automaticamente ao receber 10 peças aprovadas.")
        self._resumo(pai)
        fechadas = self.cadastro.caixas_fechadas
        if not fechadas:
            tk.Label(pai, text="Nenhuma caixa fechada ainda.", bg=FUNDO, fg=MUTED,
                     font=("Segoe UI", 12)).pack(anchor="w", pady=10)
        else:
            colunas = ("caixa", "quantidade", "ids")
            tabela = ttk.Treeview(pai, columns=colunas, show="headings")
            for coluna, titulo, largura in (("caixa", "Caixa", 100),
                                            ("quantidade", "Peças", 100),
                                            ("ids", "IDs das peças", 450)):
                tabela.heading(coluna, text=titulo)
                tabela.column(coluna, width=largura, stretch=coluna == "ids")
            for numero_caixa, pecas in enumerate(fechadas, 1):
                tabela.insert("", "end", values=(numero_caixa, len(pecas),
                                                 ", ".join(peca.id for peca in pecas)))
            tabela.pack(fill="both", expand=True)
        aberta = self.cadastro.caixa_aberta
        tk.Label(pai, text=(f"Caixa aberta: {len(aberta)}/10 peças" if aberta else "Nenhuma caixa aberta"),
                 bg=FUNDO, fg=AZUL, font=("Segoe UI Semibold", 11)).pack(anchor="w", pady=(16, 0))

    def _texto_relatorio(self) -> str:
        dados = self.cadastro.relatorio()
        linhas = [
            "RELATÓRIO FINAL — CONTROLE DE PEÇAS",
            "=" * 44,
            f"Total de peças cadastradas: {dados['total']}",
            f"Total de peças aprovadas: {dados['aprovadas']}",
            f"Total de peças reprovadas: {dados['reprovadas']}",
            f"Caixas fechadas: {dados['caixas_fechadas']}",
            f"Peças na caixa aberta: {dados['caixa_aberta']}",
            f"Quantidade de caixas utilizadas: {dados['caixas_utilizadas']}",
            "",
            "MOTIVOS DE REPROVAÇÃO (ocorrências)",
        ]
        if dados["motivos"]:
            linhas.extend(f"• {motivo}: {quantidade}" for motivo, quantidade in dados["motivos"].items())
        else:
            linhas.append("Nenhuma peça reprovada.")
        linhas.extend(["", "PEÇAS REPROVADAS E SEUS MOTIVOS"])
        if dados["pecas_reprovadas"]:
            linhas.extend(f"• {item['id']}: {'; '.join(item['motivos'])}"
                         for item in dados["pecas_reprovadas"])
        else:
            linhas.append("Nenhuma peça reprovada.")
        linhas.extend(["", "QUANTIDADE POR NOME"])
        if dados["por_nome"]:
            linhas.extend(
                f"• {item['nome']}: {item['total']} no total, "
                f"{item['aprovadas']} aprovada(s), {item['reprovadas']} reprovada(s)"
                for item in dados["por_nome"]
            )
        else:
            linhas.append("Nenhuma peça cadastrada.")
        return "\n".join(linhas)

    def mostrar_relatorio(self) -> None:
        pai = self._limpar("Relatório final", "Resumo consolidado da produção, das caixas e dos motivos de reprovação.")
        self._resumo(pai)
        area = tk.Text(pai, wrap="word", font=("Consolas", 10), bg=BRANCO, fg=TEXTO,
                       relief="flat", padx=20, pady=18, spacing1=3)
        area.insert("1.0", self._texto_relatorio())
        area.configure(state="disabled")
        area.pack(fill="both", expand=True)

        def exportar() -> None:
            caminho = filedialog.asksaveasfilename(parent=self, title="Salvar relatório",
                                                    defaultextension=".txt",
                                                    filetypes=[("Arquivo de texto", "*.txt")],
                                                    initialfile="relatorio_pecas.txt")
            if not caminho:
                return
            try:
                Path(caminho).write_text(self._texto_relatorio(), encoding="utf-8")
            except OSError as erro:
                messagebox.showerror("Erro ao exportar", str(erro), parent=self)
                return
            messagebox.showinfo("Relatório salvo", f"Arquivo salvo em:\n{caminho}", parent=self)

        self._botao(pai, "Exportar relatório (.txt)", exportar, True).pack(anchor="w", pady=(16, 0))


def main() -> None:
    arquivo = ArquivoCadastro(Path(__file__).with_name("dados_pecas.json"))
    try:
        cadastro = arquivo.carregar()
    except ValueError as erro:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Erro ao abrir dados", str(erro), parent=raiz)
        raiz.destroy()
        return
    Aplicativo(cadastro, arquivo).mainloop()


if __name__ == "__main__":
    main()
