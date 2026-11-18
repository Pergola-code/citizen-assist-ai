"""
main.py
Ponto de entrada do Citizen Assist AI. Execute com:  python main.py
"""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente, ler_opcao

# Caminhos montados a partir da pasta deste arquivo. Assim o programa
# encontra a pasta data/ mesmo se for executado de outra pasta do terminal.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA_PROJETO, "data")
CAMINHO_BASE = os.path.join(PASTA_DADOS, "base_conhecimento.csv")


def mostrar_menu():
    print("\n========== MENU ==========")
    print("1 - Fazer uma pergunta")
    print("2 - Navegar por categorias")
    print("3 - Ver indicadores")
    print("4 - Exportar atendimentos (CSV)")
    print("5 - Recarregar base de conhecimento")
    print("0 - Sair")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    base.carregar()        # usa open(), for e split() para ler a base

    assistente = Assistente("Citizen Assist AI", base, PASTA_DADOS)
    assistente.boas_vindas()

    while True:
        mostrar_menu()
        opcao = ler_opcao("Escolha uma opção: ", 0, 5)

        if opcao == 1:
            assistente.perguntar()     # usa base.buscar() e orientacao.exibir()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        elif opcao == 5:
            # Útil para editar o CSV com o programa aberto (ex.: nova palavra-chave)
            if base.carregar():
                print(f"Base recarregada: {len(base.orientacoes)} orientações.")
        else:
            assistente.pedir_nota()
            assistente.exportar_csv()
            print("\nObrigado por usar o Citizen Assist AI. Até logo!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: encerra com educação, sem mostrar erro.
        print("\n\nAtendimento encerrado. Até logo!")
