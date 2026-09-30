# Controle de Peças: Qualidade e Armazenamento

Protótipo em Python com interface gráfica para cadastrar peças, avaliar a qualidade da produção, organizar as peças aprovadas em caixas e gerar relatórios.

## Requisitos

- Python 3.10 ou superior, com Tkinter (incluído na instalação padrão do Python para Windows).
- Nenhuma biblioteca externa é necessária.

## Como executar

1. Baixe os arquivos do repositório para uma pasta.
2. Abra o terminal nessa pasta.
3. Execute:

   ```powershell
   py app.py
   ```

   Se `py` não estiver disponível, tente `python app.py`.

O aplicativo cria `dados_pecas.json` na mesma pasta quando a primeira peça é cadastrada. Os dados são carregados automaticamente na próxima execução. Esse arquivo contém dados locais e não deve ser publicado no repositório.

## Funções da interface

| Opção | O que faz |
| --- | --- |
| 1. Cadastrar nova peça | Recebe nome, quantidade, peso, cor e comprimento; gera os IDs e mostra aprovação ou todos os motivos de reprovação. |
| 2. Listar peças | Exibe cada unidade com ID próprio, permite filtrar aprovadas ou reprovadas e remover a selecionada. |
| 3. Remover peça | Abre a mesma lista, onde a peça pode ser selecionada e removida após confirmação. |
| 4. Caixas fechadas | Lista as caixas completas e os IDs das 10 peças de cada uma. |
| 5. Relatório final | Mostra totais, caixas utilizadas e motivos de cada peça reprovada; permite exportar um `.txt`. |

Há também uma visão geral e o botão **Sair**.

## Regras de qualidade e armazenamento

Uma peça é aprovada se **todas** as condições forem verdadeiras:

- Peso entre **95 g e 105 g**, inclusive.
- Cor **azul** ou **verde**, escolhida em uma lista. As outras opções reprovam a peça por cor.
- Comprimento entre **10 cm e 20 cm**, inclusive.

Valores decimais podem usar vírgula ou ponto. Campos numéricos inválidos e números menores ou iguais a zero são recusados. Uma cor diferente de azul ou verde é um dado válido, mas reprova a peça. Se uma peça falhar em dois ou três critérios, **todos os motivos** aparecem na lista e no relatório.

O **nome** identifica o tipo ou modelo da peça; o **ID** identifica uma unidade específica. Informe uma quantidade inteira de 1 a 1000. Para três unidades, o programa gera `P000001`, `P000002` e `P000003`. A numeração é global, automática e continua mesmo depois de remover peças ou fechar e reabrir o aplicativo. Cada unidade permanece em uma linha própria, e o relatório soma as quantidades por nome. Também é possível remover uma unidade específica sem apagar as demais.

A cada 10 peças aprovadas, uma caixa é fechada. Peças reprovadas não ocupam caixas. O relatório conta como **caixa utilizada** cada caixa fechada e também a caixa aberta, caso contenha ao menos uma peça. Quando uma peça é removida, as aprovadas restantes são reorganizadas na ordem de cadastro; isso pode alterar as caixas fechadas. Trata-se de uma simulação lógica, sem controle físico de estoque.

Os dados ficam em `dados_pecas.json`, um arquivo **JSON local**, e não em um banco de dados. O programa salva após cada cadastro ou remoção e carrega o arquivo ao abrir. O próximo número de ID também é salvo. Cadastros feitos na versão inicial, sem o campo nome, continuam legíveis; nesses registros, o nome é apresentado como o ID.

## Exemplos de entradas e saídas

**Exemplo 1: peça aprovada**

```text
Nome: Parafuso M4
Quantidade: 2
Peso (g): 100,5
Cor: azul
Comprimento (cm): 15
Resultado: 2 peças aprovadas e armazenadas.
IDs: P000001 e P000002
```

**Exemplo 2: peça com mais de um motivo de reprovação**

```text
Nome: Arruela
Quantidade: 1
Peso (g): 94
Cor: vermelho
Comprimento (cm): 21
Resultado: Peça reprovada: peso fora de 95 a 105 g;
           cor diferente de azul ou verde;
           comprimento fora de 10 a 20 cm.
```

**Exemplo 3: fechamento de caixa**

Após cadastrar 10 peças aprovadas, inclusive por meio de um lote, a tela **Caixas fechadas** mostra a caixa 1 com 10 IDs. A décima primeira peça aprovada fica em uma nova caixa aberta (1/10). O relatório indica **2 caixas utilizadas**.

## Estrutura do projeto

```text
app.py                        Interface gráfica Tkinter
controle_pecas.py             Validação, regras, caixas, relatório e persistência
tests/test_controle_pecas.py  Testes das regras principais
README.md                     Instruções, regras e exemplos
.gitignore                    Exclui dados locais e arquivos do trabalho escrito
```

## Testes

Na pasta do projeto, execute:

```powershell
py -m unittest discover -s tests -v
```

Os testes cobrem limites das regras, reprovação por cor e múltiplos motivos, lotes e IDs individuais, soma por nome, fechamento e reorganização de caixas, validação de dados, persistência e leitura de dados antigos.
