"""Regras de qualidade, organização das caixas e armazenamento local."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re


CAPACIDADE_CAIXA = 10
PESO_MIN = Decimal("95")
PESO_MAX = Decimal("105")
COMPRIMENTO_MIN = Decimal("10")
COMPRIMENTO_MAX = Decimal("20")
CORES_APROVADAS = {"azul", "verde"}


def ler_numero(valor: str, nome: str) -> Decimal:
    """Aceita ponto ou vírgula decimal e rejeita números inválidos."""
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{nome} deve ser um número válido.") from None
    if not numero.is_finite() or numero <= 0:
        raise ValueError(f"{nome} deve ser maior que zero.")
    return numero


@dataclass(frozen=True)
class Peca:
    id: str
    peso: Decimal
    cor: str
    comprimento: Decimal
    nome: str

    @classmethod
    def criar(cls, id: str, peso: str, cor: str, comprimento: str,
              nome: str | None = None) -> "Peca":
        identificador = str(id).strip()
        cor_normalizada = str(cor).strip().casefold()
        nome_normalizado = str(nome).strip() if nome is not None else identificador
        if not identificador:
            raise ValueError("Informe o ID da peça.")
        if not nome_normalizado:
            raise ValueError("Informe o nome da peça.")
        if not cor_normalizada:
            raise ValueError("Informe a cor da peça.")
        return cls(
            identificador,
            ler_numero(peso, "Peso"),
            cor_normalizada,
            ler_numero(comprimento, "Comprimento"),
            nome_normalizado,
        )

    @property
    def motivos_reprovacao(self) -> tuple[str, ...]:
        motivos = []
        if not PESO_MIN <= self.peso <= PESO_MAX:
            motivos.append("peso fora de 95 a 105 g")
        if self.cor not in CORES_APROVADAS:
            motivos.append("cor diferente de azul ou verde")
        if not COMPRIMENTO_MIN <= self.comprimento <= COMPRIMENTO_MAX:
            motivos.append("comprimento fora de 10 a 20 cm")
        return tuple(motivos)

    @property
    def aprovada(self) -> bool:
        return not self.motivos_reprovacao

    def serializar(self) -> dict[str, str]:
        return {
            "id": self.id,
            "peso": str(self.peso),
            "cor": self.cor,
            "comprimento": str(self.comprimento),
            "nome": self.nome,
        }


class Cadastro:
    """Mantém a ordem de cadastro; caixas são reorganizadas após remoções."""

    def __init__(self, pecas: list[Peca] | None = None, proximo_id: int = 1):
        self.pecas = list(pecas or [])
        ids = [peca.id.casefold() for peca in self.pecas]
        if len(ids) != len(set(ids)):
            raise ValueError("O arquivo contém IDs de peças repetidos.")
        if not isinstance(proximo_id, int) or proximo_id < 1:
            raise ValueError("Próximo ID inválido no arquivo de dados.")
        numeros = [int(peca.id[1:]) for peca in self.pecas
                   if re.fullmatch(r"P\d+", peca.id, flags=re.IGNORECASE)]
        self.proximo_id = max(proximo_id, max(numeros, default=0) + 1)

    @property
    def aprovadas(self) -> list[Peca]:
        return [peca for peca in self.pecas if peca.aprovada]

    @property
    def reprovadas(self) -> list[Peca]:
        return [peca for peca in self.pecas if not peca.aprovada]

    @property
    def caixas_fechadas(self) -> list[list[Peca]]:
        aprovadas = self.aprovadas
        return [
            aprovadas[i : i + CAPACIDADE_CAIXA]
            for i in range(0, len(aprovadas) - len(aprovadas) % CAPACIDADE_CAIXA, CAPACIDADE_CAIXA)
        ]

    @property
    def caixa_aberta(self) -> list[Peca]:
        aprovadas = self.aprovadas
        quantidade = len(aprovadas) % CAPACIDADE_CAIXA
        return aprovadas[-quantidade:] if quantidade else []

    @property
    def caixas_utilizadas(self) -> int:
        return len(self.caixas_fechadas) + bool(self.caixa_aberta)

    def adicionar(self, peca: Peca) -> None:
        if any(item.id.casefold() == peca.id.casefold() for item in self.pecas):
            raise ValueError(f"Já existe uma peça com o ID '{peca.id}'.")
        self.pecas.append(peca)
        if re.fullmatch(r"P\d+", peca.id, flags=re.IGNORECASE):
            self.proximo_id = max(self.proximo_id, int(peca.id[1:]) + 1)

    def adicionar_lote(self, nome: str, peso: str, cor: str,
                       comprimento: str, quantidade: str | int) -> list[Peca]:
        """Cria um registro e ID único para cada unidade de um lote."""
        if not str(quantidade).strip().isdecimal():
            raise ValueError("Quantidade deve ser um número inteiro positivo.")
        total = int(str(quantidade).strip())
        if not 1 <= total <= 1000:
            raise ValueError("Quantidade deve estar entre 1 e 1000.")
        modelo = Peca.criar("P000001", peso, cor, comprimento, nome)
        criadas = []
        for _ in range(total):
            identificador = f"P{self.proximo_id:06d}"
            peca = Peca(identificador, modelo.peso, modelo.cor,
                        modelo.comprimento, modelo.nome)
            self.adicionar(peca)
            criadas.append(peca)
        return criadas

    def remover(self, identificador: str) -> Peca:
        for indice, peca in enumerate(self.pecas):
            if peca.id.casefold() == identificador.strip().casefold():
                return self.pecas.pop(indice)
        raise ValueError(f"Peça '{identificador}' não encontrada.")

    def relatorio(self) -> dict:
        contagem = Counter(
            motivo for peca in self.reprovadas for motivo in peca.motivos_reprovacao
        )
        por_nome = {}
        for peca in self.pecas:
            chave = peca.nome.casefold()
            if chave not in por_nome:
                por_nome[chave] = {"nome": peca.nome, "total": 0,
                                   "aprovadas": 0, "reprovadas": 0}
            por_nome[chave]["total"] += 1
            por_nome[chave]["aprovadas" if peca.aprovada else "reprovadas"] += 1
        return {
            "total": len(self.pecas),
            "aprovadas": len(self.aprovadas),
            "reprovadas": len(self.reprovadas),
            "caixas_fechadas": len(self.caixas_fechadas),
            "caixa_aberta": len(self.caixa_aberta),
            "caixas_utilizadas": self.caixas_utilizadas,
            "motivos": dict(contagem),
            "por_nome": list(por_nome.values()),
            "pecas_reprovadas": [
                {"id": peca.id, "motivos": list(peca.motivos_reprovacao)}
                for peca in self.reprovadas
            ],
        }


class ArquivoCadastro:
    def __init__(self, caminho: Path):
        self.caminho = Path(caminho)

    def carregar(self) -> Cadastro:
        if not self.caminho.exists():
            return Cadastro()
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            if dados.get("versao") != 1 or not isinstance(dados.get("pecas"), list):
                raise ValueError("Formato do arquivo não reconhecido.")
            return Cadastro([Peca.criar(**item) for item in dados["pecas"]],
                            dados.get("proximo_id", 1))
        except (OSError, json.JSONDecodeError, TypeError, KeyError, ValueError) as erro:
            raise ValueError(f"Não foi possível carregar {self.caminho}: {erro}") from erro

    def salvar(self, cadastro: Cadastro) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_suffix(self.caminho.suffix + ".tmp")
        conteudo = {"versao": 1, "proximo_id": cadastro.proximo_id,
                    "pecas": [peca.serializar() for peca in cadastro.pecas]}
        temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(self.caminho)
