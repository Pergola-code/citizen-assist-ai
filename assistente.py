"""
assistente.py
Classe Assistente: conversa com o cidadão, guarda o histórico de atendimentos,
calcula indicadores e exporta CSV. Também tem as funções que validam a entrada.
"""

import os
import time
from datetime import datetime

from base_conhecimento import normalizar

# Limites de confiança (pontos da melhor orientação)
LIMITE_ALTA = 6    # 6 ou mais  -> ALTA
LIMITE_MEDIA = 3   # 3 a 5      -> MÉDIA  | menos de 3 -> "não encontrei"
MAX_ALTERNATIVAS = 2

MAX_DIGITOS = 8    # 8 ou mais dígitos na pergunta = possível CPF/telefone

CAMPOS_HISTORICO = ["data", "origem", "pergunta", "id_orientacao",
                    "encontrou", "ajudou", "tentativas", "tempo_s"]


# ---------------------------------------------------------------------- #
# Funções de validação de entrada (nenhuma entrada inválida encerra o programa)
# ---------------------------------------------------------------------- #
def ler_opcao(mensagem, minimo, maximo):
    """Pede um número inteiro entre minimo e maximo e só sai quando for válido."""
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            print("Resposta vazia. Digite um número.")
            continue
        if not texto.isdigit():          # pega letras, sinais, números negativos...
            print(f"'{texto}' não é uma opção válida. Digite um número de {minimo} a {maximo}.")
            continue
        numero = int(texto)
        if numero < minimo or numero > maximo:
            print(f"Opção fora da faixa. Digite um número de {minimo} a {maximo}.")
            continue
        return numero


def ler_sim_nao(mensagem):
    """Aceita s/n (e sim/não). Devolve True para sim e False para não."""
    while True:
        resposta = normalizar(input(mensagem)).strip()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


def contem_dado_pessoal(texto):
    """Detecta possível CPF, telefone (8+ dígitos) ou e-mail (@)."""
    quantidade_digitos = sum(1 for caractere in texto if caractere.isdigit())
    return quantidade_digitos >= MAX_DIGITOS or "@" in texto


def limpar_campo(texto):
    """Tira ';' e quebras de linha para não estragar o CSV."""
    return texto.replace(";", ",").replace("\n", " ").replace("\r", " ").strip()


# ---------------------------------------------------------------------- #
# Classe principal
# ---------------------------------------------------------------------- #
class Assistente:
    """Quem conversa com o cidadão. Composição: o Assistente TEM uma BaseConhecimento."""

    def __init__(self, nome, base, pasta_dados="data"):
        self.nome = nome
        self.base = base                 # objeto BaseConhecimento
        self.historico = []              # lista de dicionários (um por atendimento)
        self.notas = []                  # notas de facilidade (1 a 5)
        self.caminho_historico = os.path.join(pasta_dados, "historico.csv")
        self.caminho_exportacao = os.path.join(pasta_dados, "atendimentos.csv")
        self.caminho_notas = os.path.join(pasta_dados, "avaliacoes.csv")
        os.makedirs(pasta_dados, exist_ok=True)
        self._carregar_historico()
        self._carregar_notas()

    # ------------------------------------------------------------------ #
    # Telas
    # ------------------------------------------------------------------ #
    def boas_vindas(self):
        print("=" * 64)
        print(f"  {self.nome} - orientação para jovens no primeiro emprego")
        print("=" * 64)
        print("Tiro dúvidas sobre documentos, trabalho, benefícios e serviços digitais.")
        print("Privacidade: NÃO digite nome, CPF, telefone ou e-mail.")
        print("Este assistente NÃO é um canal oficial. Confirme sempre na fonte indicada.")
        print(f"Orientações carregadas: {len(self.base.orientacoes)}")

    @staticmethod
    def confianca(pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return "BAIXA"

    def _base_vazia(self):
        if not self.base.orientacoes:
            print("\nA base de conhecimento está vazia ou não foi carregada.")
            print("Verifique o arquivo data/base_conhecimento.csv e use a opção 'Recarregar base'.")
            return True
        return False

    def _mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Dica: use palavras mais diretas, como 'CPF', 'título de eleitor', 'estágio'.")
        print("Você também pode navegar por estas categorias: " + ", ".join(self.base.categorias()))

    # ------------------------------------------------------------------ #
    # Atendimento por pergunta em texto livre
    # ------------------------------------------------------------------ #
    def perguntar(self):
        """Tela de perguntas: faz um atendimento atrás do outro até a pessoa digitar 0."""
        if self._base_vazia():
            return

        print("\n--- Fazer uma pergunta ---")
        print("Pergunte do seu jeito, por exemplo: 'como tiro meu primeiro título de eleitor?'")
        while self._atendimento_por_pergunta():
            pass  # dúvida resolvida -> começa um novo atendimento

    def _atendimento_por_pergunta(self):
        """UM atendimento. Pode ter várias tentativas (a pessoa reformula a pergunta).

        Devolve True se a dúvida foi resolvida e False se a pessoa digitou 0.
        """
        inicio = time.time()          # começa a contar o tempo do atendimento
        tentativas = 0
        ultima_pergunta = ""
        ultimo_id = ""
        encontrou_algo = False

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                break
            if normalizar(pergunta).strip() == "":   # vazio ou só pontuação
                print("Você não digitou nenhuma dúvida. Escreva com palavras ou 0 para voltar.")
                continue
            if contem_dado_pessoal(pergunta):
                # Recusada e NÃO registrada: não guardamos dados pessoais.
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)   # lista de tuplas (pontos, orientacao)

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                self._mostrar_nao_encontrei()
                continue

            pontos, melhor = resultados[0]            # desempacotando a tupla
            encontrou_algo = True
            ultimo_id = melhor.id
            print(f"\nConfiança da resposta: {self.confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            # Até duas alternativas (as próximas da lista que também passaram do limite)
            alternativas = [(p, o) for p, o in resultados[1:] if p >= LIMITE_MEDIA][:MAX_ALTERNATIVAS]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for numero, (p, o) in enumerate(alternativas, start=1):
                    print(f"  {numero} - {o.titulo} [{o.categoria}] ({p} pontos)")

            if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("pergunta", pergunta, melhor.id, True, True, tentativas, inicio)
                print("Que bom! Atendimento registrado.")
                return True

            # Não ajudou: a pessoa pode abrir uma alternativa ou reformular
            if alternativas:
                escolha = ler_opcao("Digite o número de uma alternativa para vê-la "
                                    "(0 para reformular a pergunta): ", 0, len(alternativas))
                if escolha != 0:
                    escolhida = alternativas[escolha - 1][1]
                    ultimo_id = escolhida.id
                    escolhida.exibir()
                    if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                        self.registrar("pergunta", pergunta, escolhida.id, True, True,
                                       tentativas, inicio)
                        print("Que bom! Atendimento registrado.")
                        return True

            print("Tudo bem. Tente escrever a dúvida de outro jeito.")

        # Saiu com 0: se a pessoa chegou a perguntar algo, registramos como não resolvido
        if tentativas > 0:
            self.registrar("pergunta", ultima_pergunta, ultimo_id, encontrou_algo, False,
                           tentativas, inicio)
            print("Atendimento registrado como 'sem solução'. Obrigado por avisar!")
        return False

    # ------------------------------------------------------------------ #
    # Atendimento por navegação em categorias
    # ------------------------------------------------------------------ #
    def navegar(self):
        if self._base_vazia():
            return

        inicio = time.time()
        while True:
            categorias = self.base.categorias()
            print("\n--- Categorias ---")
            for numero, categoria in enumerate(categorias, start=1):
                quantidade = len(self.base.por_categoria(categoria))
                print(f"{numero} - {categoria} ({quantidade} orientações)")
            print("0 - Voltar")
            opcao = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return

            categoria = categorias[opcao - 1]
            while True:
                lista = self.base.por_categoria(categoria)
                print(f"\n--- {categoria} ---")
                for numero, orientacao in enumerate(lista, start=1):
                    print(f"{numero} - {orientacao.titulo}")
                print("0 - Voltar")
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(lista))
                if escolha == 0:
                    break

                orientacao = lista[escolha - 1]
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", f"{categoria} > {orientacao.titulo}",
                               orientacao.id, True, ajudou, 1, inicio)
                print("Atendimento registrado.")
                inicio = time.time()   # o próximo atendimento começa a contar agora

    # ------------------------------------------------------------------ #
    # Histórico
    # ------------------------------------------------------------------ #
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, inicio):
        """Salva um atendimento na memória (self.historico) e em data/historico.csv."""
        if contem_dado_pessoal(pergunta):
            return  # segunda barreira: dado pessoal nunca vai para o arquivo

        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": limpar_campo(pergunta),
            "id_orientacao": str(id_orientacao),
            "encontrou": "sim" if encontrou else "nao",
            "ajudou": "sim" if ajudou else "nao",
            "tentativas": tentativas,
            "tempo_s": round(time.time() - inicio, 1),
        }
        self.historico.append(registro)
        self._anexar_no_historico(registro)

    def _anexar_no_historico(self, registro):
        """Acrescenta UMA linha no fim do historico.csv (modo 'a' = append)."""
        try:
            arquivo_novo = (not os.path.exists(self.caminho_historico)
                            or os.path.getsize(self.caminho_historico) == 0)
            with open(self.caminho_historico, "a", encoding="utf-8") as arquivo:
                if arquivo_novo:
                    arquivo.write(";".join(CAMPOS_HISTORICO) + "\n")
                valores = [str(registro[campo]) for campo in CAMPOS_HISTORICO]
                arquivo.write(";".join(valores) + "\n")
        except OSError:
            print("[AVISO] Não foi possível salvar no histórico. O atendimento continua.")

    def _carregar_historico(self):
        """Lê o historico.csv de execuções anteriores (se existir) para os indicadores."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                for numero_linha, linha in enumerate(arquivo, start=1):
                    linha = linha.strip()
                    if numero_linha == 1 or linha == "":
                        continue
                    campos = linha.split(";")
                    if len(campos) != len(CAMPOS_HISTORICO):
                        continue  # linha estragada: ignora sem quebrar
                    registro = dict(zip(CAMPOS_HISTORICO, campos))
                    try:
                        registro["tentativas"] = int(registro["tentativas"])
                        registro["tempo_s"] = float(registro["tempo_s"])
                    except ValueError:
                        continue
                    self.historico.append(registro)
        except FileNotFoundError:
            pass  # primeira execução: ainda não existe histórico
        except (OSError, UnicodeDecodeError):
            print("[AVISO] historico.csv não pôde ser lido. Começando um histórico novo na memória.")

    # ------------------------------------------------------------------ #
    # Nota de facilidade
    # ------------------------------------------------------------------ #
    def pedir_nota(self):
        print("\nAntes de sair: de 1 a 5, quão fácil foi usar o assistente?")
        print("(1 = muito difícil, 5 = muito fácil, 0 = pular)")
        nota = ler_opcao("Sua nota: ", 0, 5)
        if nota == 0:
            return
        self.notas.append(nota)
        try:
            arquivo_novo = not os.path.exists(self.caminho_notas)
            with open(self.caminho_notas, "a", encoding="utf-8") as arquivo:
                if arquivo_novo:
                    arquivo.write("data;nota\n")
                arquivo.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{nota}\n")
        except OSError:
            print("[AVISO] Não foi possível salvar a nota.")
        print("Obrigado pela avaliação!")

    def _carregar_notas(self):
        try:
            with open(self.caminho_notas, "r", encoding="utf-8") as arquivo:
                for numero_linha, linha in enumerate(arquivo, start=1):
                    partes = linha.strip().split(";")
                    if numero_linha == 1 or len(partes) != 2:
                        continue
                    if partes[1].isdigit() and 1 <= int(partes[1]) <= 5:
                        self.notas.append(int(partes[1]))
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            pass

    # ------------------------------------------------------------------ #
    # Indicadores
    # ------------------------------------------------------------------ #
    def indicadores(self):
        """Calcula, exibe e devolve (em dicionário) os indicadores do assistente."""
        print("\n--- Indicadores ---")
        total = len(self.historico)
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return {}

        encontrados = [r for r in self.historico if r["encontrou"] == "sim"]
        resolvidos = [r for r in self.historico if r["ajudou"] == "sim"]

        resultado = {
            "total": total,
            "encontrada_pct": len(encontrados) / total * 100,
            "acerto_pct": len(resolvidos) / total * 100,
            # tempo médio só dos atendimentos em que a pessoa resolveu a dúvida
            "tempo_medio": (sum(r["tempo_s"] for r in resolvidos) / len(resolvidos)
                            if resolvidos else 0.0),
            "tentativas_media": sum(r["tentativas"] for r in self.historico) / total,
            "facilidade": sum(self.notas) / len(self.notas) if self.notas else None,
            "sem_solucao": [],
        }
        for r in self.historico:
            if r["ajudou"] == "nao" and r["pergunta"] not in resultado["sem_solucao"]:
                resultado["sem_solucao"].append(r["pergunta"])

        print(f"Atendimentos registrados ........ {total}")
        print(f"Resposta encontrada ............. {resultado['encontrada_pct']:.1f}%")
        print(f"Taxa de acerto (ajudou) ......... {resultado['acerto_pct']:.1f}%")
        print(f"Tempo médio para encontrar ...... {resultado['tempo_medio']:.1f} s")
        print(f"Tentativas por atendimento ...... {resultado['tentativas_media']:.2f}")
        if resultado["facilidade"] is None:
            print("Facilidade de uso (1 a 5) ....... sem avaliações ainda")
        else:
            print(f"Facilidade de uso (1 a 5) ....... {resultado['facilidade']:.1f} "
                  f"({len(self.notas)} avaliação(ões))")
        print("Dúvidas sem solução:")
        if resultado["sem_solucao"]:
            for pergunta in resultado["sem_solucao"]:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")
        return resultado

    # ------------------------------------------------------------------ #
    # Exportação
    # ------------------------------------------------------------------ #
    def exportar_csv(self):
        """Exporta todos os atendimentos para data/atendimentos.csv com open() e write()."""
        cabecalho = CAMPOS_HISTORICO[:4] + ["titulo_orientacao", "categoria"] + CAMPOS_HISTORICO[4:]
        try:
            with open(self.caminho_exportacao, "w", encoding="utf-8") as arquivo:
                arquivo.write(";".join(cabecalho) + "\n")
                for r in self.historico:
                    titulo, categoria = "", ""
                    if r["id_orientacao"].isdigit():
                        orientacao = self.base.buscar_por_id(int(r["id_orientacao"]))
                        if orientacao is not None:
                            titulo, categoria = orientacao.titulo, orientacao.categoria
                    linha = [r["data"], r["origem"], r["pergunta"], r["id_orientacao"],
                             titulo, categoria, r["encontrou"], r["ajudou"],
                             str(r["tentativas"]), str(r["tempo_s"])]
                    arquivo.write(";".join(linha) + "\n")
        except OSError:
            print("[ERRO] Não foi possível exportar o arquivo.")
            return 0
        print(f"\n{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_exportacao}")
        return len(self.historico)
