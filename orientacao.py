"""
orientacao.py
Classe Orientacao: representa UMA orientação da base de conhecimento,
ou seja, UMA linha do arquivo data/base_conhecimento.csv.
"""

AVISO_OFICIAL = "Aviso: este assistente NÃO é um canal oficial. Confirme sempre na fonte."


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # 'self' é o próprio objeto que está sendo criado.
        # Cada atributo abaixo fica "grudado" nesse objeto, então cada
        # orientação tem os seus próprios valores.
        self.id = id                          # int  -> número da orientação
        self.categoria = categoria            # str  -> ex.: "Documentos"
        self.titulo = titulo                  # str  -> ex.: "Tirar o CPF"
        self.palavras_chave = palavras_chave  # list -> ex.: ["cpf", "tirar o cpf"]
        self.resposta = resposta              # str  -> texto em linguagem simples
        self.documentos = documentos          # list -> documentos necessários
        self.onde = onde                      # str  -> onde a pessoa deve ir
        self.fonte = fonte                    # str  -> link oficial
        self.verificado_em = verificado_em    # str  -> data em que conferimos (AAAA-MM-DD)

    def exibir(self):
        """Mostra a orientação completa, sempre com fonte, data e aviso."""
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(self.resposta)

        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")

        print(f"Onde: {self.onde}")
        # Transparência: toda resposta mostra de onde veio e quando foi conferida.
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO_OFICIAL)

    def __str__(self):
        # Usado quando fazemos print(orientacao) ou f"{orientacao}".
        return f"{self.id} - {self.titulo} [{self.categoria}]"
