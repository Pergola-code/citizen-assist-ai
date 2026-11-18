"""
base_conhecimento.py
Função normalizar() e classe BaseConhecimento: lê o CSV, lista categorias
e faz a busca com pontuação ("inteligência" baseada em regras).
"""

from orientacao import Orientacao

# Campos esperados no cabeçalho do CSV, na ordem certa.
CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

# Pesos e limites da pontuação (ficam em constantes para ser fácil ajustar).
PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação aparece na pergunta
PONTOS_TITULO = 1          # palavra da pergunta (4+ letras) aparece no título
TAMANHO_MINIMO_TITULO = 4

# Palavras muito comuns que NÃO devem dar ponto no título
# (ex.: "como", "fazer"). Sem isso, perguntas genéricas pontuariam à toa.
PALAVRAS_IGNORADAS = {"como", "para", "fazer", "onde", "qual", "quais", "quero",
                      "preciso", "posso", "pode", "minha", "sobre", "tenho",
                      "isso", "esse", "essa", "pelo", "pela", "quando", "ainda"}

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u", "ç": "c"}

# Além dos sinais do enunciado, tratamos "-", "/" e aspas como espaço,
# para que "meia-entrada" vire "meia entrada" e "gov.br" vire "gov br".
SINAIS = "?!.,;:()-/\"'"


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.

    Devolve com um espaço no começo e no fim. Isso é proposital: assim,
    procurar " sus " dentro de " como faco o cartao do sus " só encontra
    a PALAVRA inteira "sus", e não um pedaço de outra palavra (ex.: "susto").
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    # split() sem argumento quebra em qualquer quantidade de espaços,
    # e o join junta de volta com UM espaço só.
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Conjunto de todas as orientações (composição: tem uma lista de Orientacao)."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []      # lista de objetos Orientacao
        self.linhas_ignoradas = 0  # quantas linhas do CSV estavam com problema

    # ------------------------------------------------------------------ #
    # Leitura do arquivo
    # ------------------------------------------------------------------ #
    def carregar(self):
        """Lê o CSV com open() + for + split(";").

        Devolve True se carregou alguma orientação, False caso contrário.
        Nunca deixa o programa quebrar: arquivo ausente ou mal formatado
        gera apenas uma mensagem de aviso.
        """
        self.orientacoes = []
        self.linhas_ignoradas = 0

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                for numero_linha, linha in enumerate(arquivo, start=1):
                    # lstrip("﻿") remove o "BOM", um caractere invisível
                    # que o Excel às vezes coloca no começo do arquivo.
                    linha = linha.strip().lstrip("﻿")

                    if numero_linha == 1:
                        if linha.split(";") != CAMPOS:
                            print(f"[ERRO] Cabeçalho inválido em '{self.caminho}'.")
                            print("       Esperado: " + ";".join(CAMPOS))
                            return False
                        continue  # o cabeçalho não é uma orientação

                    if linha == "":
                        continue  # ignora linhas em branco

                    self._ler_linha(linha, numero_linha)

        except FileNotFoundError:
            print(f"[ERRO] Arquivo '{self.caminho}' não encontrado.")
            print("       O assistente vai abrir, mas sem orientações.")
            return False
        except (UnicodeDecodeError, OSError):
            print(f"[ERRO] Não foi possível ler '{self.caminho}' (formato inválido).")
            return False

        if self.linhas_ignoradas > 0:
            print(f"[AVISO] {self.linhas_ignoradas} linha(s) do CSV foram ignoradas.")
        return len(self.orientacoes) > 0

    def _ler_linha(self, linha, numero_linha):
        """Transforma UMA linha do CSV em um objeto Orientacao."""
        campos = linha.split(";")
        if len(campos) != len(CAMPOS):
            print(f"[AVISO] Linha {numero_linha}: esperava {len(CAMPOS)} campos "
                  f"e encontrou {len(campos)}. Linha ignorada.")
            self.linhas_ignoradas += 1
            return

        # zip() junta as duas listas par a par: ("id", "1"), ("categoria", "Documentos")...
        # dict() transforma esses pares em um DICIONÁRIO: {"id": "1", "categoria": ...}
        # Assim acessamos cada campo pelo NOME, e não por um índice "mágico" como campos[3].
        registro = dict(zip(CAMPOS, [c.strip() for c in campos]))

        try:
            id_orientacao = int(registro["id"])
        except ValueError:
            print(f"[AVISO] Linha {numero_linha}: id '{registro['id']}' não é número. Linha ignorada.")
            self.linhas_ignoradas += 1
            return

        # Regra da atividade: toda orientação precisa ter fonte e data de verificação.
        if registro["fonte"] == "" or registro["verificado_em"] == "":
            print(f"[AVISO] Linha {numero_linha}: orientação sem fonte ou sem data. Linha ignorada.")
            self.linhas_ignoradas += 1
            return

        orientacao = Orientacao(
            id=id_orientacao,
            categoria=registro["categoria"],
            titulo=registro["titulo"],
            # Campos com vários itens usam "|" como separador.
            palavras_chave=self._separar_itens(registro["palavras_chave"]),
            resposta=registro["resposta"],
            documentos=self._separar_itens(registro["documentos"]),
            onde=registro["onde"],
            fonte=registro["fonte"],
            verificado_em=registro["verificado_em"],
        )
        self.orientacoes.append(orientacao)

    @staticmethod
    def _separar_itens(texto):
        """'rg|cpf| cin ' -> ['rg', 'cpf', 'cin'] (ignora itens vazios)."""
        return [item.strip() for item in texto.split("|") if item.strip() != ""]

    # ------------------------------------------------------------------ #
    # Navegação
    # ------------------------------------------------------------------ #
    def categorias(self):
        """Lista de categorias sem repetição, em ordem alfabética."""
        unicas = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in unicas:
                unicas.append(orientacao.categoria)
        return sorted(unicas)

    def por_categoria(self, categoria):
        """Todas as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def buscar_por_id(self, id_orientacao):
        for orientacao in self.orientacoes:
            if orientacao.id == id_orientacao:
                return orientacao
        return None

    # ------------------------------------------------------------------ #
    # Busca inteligente por regras
    # ------------------------------------------------------------------ #
    def pontuar(self, pergunta_normalizada, orientacao):
        """Calcula quantos pontos uma orientação recebe para a pergunta.

        Regra 1: +3 para cada palavra-chave que aparece na pergunta.
        Regra 2: +1 para cada palavra da pergunta (4+ letras) que está no título.
        """
        pontos = 0

        # Regra 1 - palavras-chave (podem ter mais de uma palavra, ex.: "titulo de eleitor").
        # Como normalizar() devolve " texto ", comparamos palavras inteiras.
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        # Regra 2 - palavras do título. Usamos set() para não contar
        # a mesma palavra duas vezes se a pessoa repetir na pergunta.
        palavras_titulo = normalizar(orientacao.titulo).split()
        for palavra in set(pergunta_normalizada.split()):
            if (len(palavra) >= TAMANHO_MINIMO_TITULO
                    and palavra not in PALAVRAS_IGNORADAS
                    and palavra in palavras_titulo):
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de TUPLAS (pontos, orientacao), da maior para a menor.

        Só entram orientações com pelo menos 1 ponto.
        """
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))  # tupla: (int, Orientacao)

        # key=lambda: ordena só pelo primeiro item da tupla (os pontos).
        # Sem isso, em caso de empate o Python tentaria comparar dois objetos
        # Orientacao e daria erro. reverse=True -> maior pontuação primeiro.
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
