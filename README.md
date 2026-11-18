# Citizen Assist AI — Primeiro Emprego

Assistente de terminal, escrito em Python, que orienta **jovens que estão entrando no mercado de trabalho** sobre documentos, trabalho, benefícios e serviços digitais do governo. Toda resposta mostra a fonte oficial, a data em que a informação foi conferida e o aviso de que o assistente **não é um canal oficial**. O assistente não coleta dados pessoais.

> GS2026.2 — Pensamento Computacional e Automação com Python (desafio CitizenTech)

---

## Integrante

| Nome | RM |
|---|---|
| Felipe Macedo | RM570990 |

Projeto feito individualmente.

---|---|
| Felipe Macedo | RM_____ |
| _(nome)_ | RM_____ |
| _(nome)_ | RM_____ |

---

## Público e problema

**Público:** jovens de 14 a 24 anos que estão tirando os primeiros documentos e procurando o primeiro emprego, estágio ou vaga de aprendiz.

**Problema:** na hora de começar a vida profissional o jovem precisa de CPF, identidade, título de eleitor, alistamento militar (homens), Carteira de Trabalho Digital e conta gov.br, e muitas vezes não sabe que tem direito a programas como Jovem Aprendiz, ID Jovem ou Cadastro Único. A informação existe, mas está espalhada em vários sites, escrita em linguagem técnica e misturada com páginas que cobram por serviços gratuitos (ex.: inscrição no CPF). O Citizen Assist AI junta essas orientações em linguagem simples, sempre apontando para a fonte oficial.

## ODS relacionados

- **ODS 8: Trabalho decente e crescimento econômico** (meta 8.6: reduzir a proporção de jovens sem emprego, educação ou formação). Orienta sobre Jovem Aprendiz, estágio e Carteira de Trabalho.
- **ODS 16: Paz, justiça e instituições eficazes** (meta 16.9: identidade legal para todos; meta 16.10: acesso público à informação). Explica como tirar documentos e mostra sempre a fonte oficial.
- **ODS 10: Redução das desigualdades** (meta 10.2: inclusão social e econômica). Divulga Cadastro Único e ID Jovem para jovens de baixa renda.

---

## Como executar

Requisitos: **Python 3.8 ou superior**. Não usa nenhuma biblioteca externa.

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py        # no Linux/Mac pode ser: python3 main.py
```

### Menu

```
1 - Fazer uma pergunta          -> busca com pontuação em texto livre
2 - Navegar por categorias      -> categorias e orientações numeradas
3 - Ver indicadores             -> métricas calculadas a partir do histórico
4 - Exportar atendimentos (CSV) -> gera data/atendimentos.csv
5 - Recarregar base             -> relê o CSV sem fechar o programa
0 - Sair                        -> pede nota de 1 a 5 e exporta o CSV
```

Em todas as telas, `0` volta para a tela anterior.

---

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                  # menu principal: cria a base e o assistente
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # normalizar() + classe BaseConhecimento
├── assistente.py            # classe Assistente + validação de entradas
└── data/
    ├── base_conhecimento.csv  # 12 orientações, 4 categorias
    ├── historico.csv          # cada atendimento (gravado na hora)
    ├── atendimentos.csv       # exportação completa (opção 4 ou ao sair)
    └── avaliacoes.csv         # notas de facilidade (1 a 5)
```

---

## Base de conhecimento (`data/base_conhecimento.csv`)

Campos separados por `;`. Campos com vários itens (`palavras_chave`, `documentos`) usam `|`.

```
id;categoria;titulo;palavras_chave;resposta;documentos;onde;fonte;verificado_em
```

| Categoria | Orientações |
|---|---|
| Documentos | 1 CPF · 2 Carteira de Identidade Nacional (CIN) · 3 Primeiro título de eleitor · 4 Alistamento militar |
| Trabalho | 5 Carteira de Trabalho Digital · 6 Jovem Aprendiz · 7 Estágio · 8 PIS e Abono Salarial |
| Benefícios | 9 Cadastro Único · 10 ID Jovem |
| Serviços Digitais | 11 Conta gov.br · 12 e-Título |

São 12 orientações em 4 categorias, cada uma com 6 ou 7 palavras-chave, fonte oficial e data de verificação.

Na leitura, cada linha é quebrada com `split(";")`. Depois, `dict(zip(CAMPOS, campos))` transforma a linha em um **dicionário** (`{"id": "1", "categoria": "Documentos", ...}`), e esse dicionário vira um objeto `Orientacao`.

**Tratamento de erros na leitura:** se o arquivo não existir, se o cabeçalho estiver errado ou se a codificação for inválida, aparece uma mensagem e o programa continua aberto, sem orientações. Linhas com número errado de campos, `id` que não é número ou sem fonte/data são ignoradas com aviso, e o resto da base é carregado normalmente.

---

## Classes e composição

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, Orientacao, ...]
```

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()`, `__str__()` |
| `BaseConhecimento` | caminho, orientacoes, linhas_ignoradas | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`, `buscar_por_id()` |
| `Assistente` | nome, base, historico, notas, caminhos dos arquivos | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `pedir_nota()`, `confianca()` |

---

## Regra de pontuação

A pergunta, as palavras-chave e o título são comparados depois de passar por `normalizar()`, que deixa o texto em minúsculas, tira acentos e pontuação e devolve com espaço no começo e no fim (ex.: `" como tiro o cpf "`). Esses espaços extras fazem a comparação valer só para **palavras inteiras**: `" sus "` não casa com `"susto"`.

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação aparece na pergunta | **+3** |
| Palavra da pergunta (4 letras ou mais) aparece no título | **+1** |
| Melhor orientação com 6 pontos ou mais | Confiança **ALTA** |
| Melhor orientação com 3 a 5 pontos | Confiança **MÉDIA** |
| Nenhuma orientação com 3 pontos | "Não encontrei" + dica + lista de categorias |

`buscar()` devolve uma lista de **tuplas** `(pontos, orientacao)` ordenada da maior para a menor pontuação. O assistente mostra a melhor e até **2 alternativas** que também tenham pelo menos 3 pontos.

**Exemplo:** `"Como tirar meu primeiro título de eleitor?"`
- palavras-chave `titulo de eleitor` (+3) e `primeiro titulo` (+3) = 6
- palavras do título `primeiro`, `titulo`, `eleitor` (+1 cada) = 3
- **Total: 9 pontos, confiança ALTA** (orientação 3)

### Ajustes que fizemos (e por quê)

1. **Palavras ignoradas no título** (`como`, `para`, `fazer`, `onde`, `quero`...): sem isso, qualquer pergunta com "como" ganharia ponto em títulos que tivessem essa palavra.
2. **Sinais extras na normalização** (`-`, `/`, aspas): assim `meia-entrada` vira `meia entrada` e `gov.br` vira `gov br`, e as duas formas casam com a palavra-chave.
3. **Palavra do título conta uma vez só** (usamos `set()`), mesmo que a pessoa repita a palavra.
4. Os pesos e limites ficam em **constantes** (`PONTOS_PALAVRA_CHAVE`, `LIMITE_ALTA`...), então dá para ajustar sem mexer na lógica.

---

## Regras de atendimento

- **Entradas inválidas:** opção fora da faixa, letras, resposta vazia e s/n inválido mostram uma mensagem e pedem de novo. Nenhuma delas encerra o programa. `Ctrl+C` fecha com uma mensagem de despedida, sem erro na tela.
- **Dados pessoais:** perguntas com 8 ou mais dígitos ou com `@` são recusadas ("não digite CPF, telefone ou e-mail") e **não são registradas**. O `registrar()` também confere isso, como segunda barreira.
- **Transparência:** toda orientação exibida mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Tentativas:** se a resposta não ajudou, a pessoa pode abrir uma alternativa ou reescrever a pergunta. Cada reescrita conta como mais uma tentativa **dentro do mesmo atendimento**.

---

## Histórico, indicadores e exportação

Cada atendimento é gravado na hora em `data/historico.csv`:

```
data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo_s
```

O tempo é medido com `inicio = time.time()` no começo e `round(time.time() - inicio, 1)` no final. O histórico é lido de novo quando o programa abre, então os indicadores juntam **todas** as execuções.

| Indicador | Como é calculado |
|---|---|
| Resposta encontrada (%) | atendimentos com orientação ≥ 3 pontos ÷ total |
| Taxa de acerto: ajudou (%) | atendimentos em que a pessoa respondeu "s" ÷ total |
| Tempo médio para encontrar | média de `tempo_s` dos atendimentos resolvidos |
| Tentativas por atendimento | soma das tentativas ÷ total |
| Facilidade de uso (1 a 5) | média das notas dadas ao sair |
| Dúvidas sem solução | perguntas dos atendimentos com `ajudou = nao` |

A exportação (`exportar_csv()`) usa `open()` e `write()` para gerar `data/atendimentos.csv`, um atendimento por linha, com o título e a categoria da orientação.

---

## Integrações com outras disciplinas

_Nenhuma nesta versão._ Se houver integração (ex.: API de IA, estruturas de Data Structures and Algorithms), descreva aqui.

---

## Fontes consultadas (verificadas em 17/11/2026)

| # | Orientação | Fonte oficial |
|---|---|---|
| 1 | CPF | https://www.gov.br/pt-br/servicos/inscrever-no-cpf |
| 2 | Carteira de Identidade Nacional | https://www.gov.br/identidade |
| 3 | Primeiro título de eleitor | https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral/autoatendimento-eleitoral-titulo-net |
| 4 | Alistamento militar | https://alistamento.eb.mil.br |
| 5 | Carteira de Trabalho Digital | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho |
| 6 | Jovem Aprendiz | https://www.gov.br/trabalho/pt-br/assuntos/aprendizagem-profissional |
| 7 | Estágio (Lei 11.788/2008) | https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm |
| 8 | PIS e Abono Salarial | https://www.gov.br/trabalho-e-emprego/pt-br |
| 9 | Cadastro Único | https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal |
| 10 | ID Jovem | https://idjovem.juventude.gov.br |
| 11 | Conta gov.br | https://www.gov.br/gestao/pt-br/assuntos/noticias/2026/marco/gov-br-alcanca-a-marca-de-175-milhoes-de-usuarios |
| 12 | e-Título | https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral/autoatendimento-eleitoral-titulo-net |

---

## Resultado dos testes com participantes reais

> **Transparência:** os testes foram realizados com três pessoas reais: Angelica, Eduardo e Rosana. Os participantes utilizaram o Citizen Assist AI e avaliaram a experiência de uso. O histórico, os tempos e os indicadores apresentados abaixo foram registrados pelo próprio programa em `data/historico.csv`.

**Como foi feito:** foram realizadas 3 sessões de teste, uma com cada participante. Durante as sessões, os participantes utilizaram o programa para consultar temas relacionados a documentos, trabalho, benefícios e serviços digitais. No total, foram registrados 12 atendimentos: 11 por pergunta e 1 por navegação por categoria.

| Participante | Idade | Situações testadas | Nota |
|---|---:|---|---:|
| Angelica | 17 anos | Carteira de Trabalho, título de eleitor, estágio, seguro-desemprego | 4 |
| Eduardo | 18 anos | Meia-entrada, alistamento, novo RG, 2ª via da identidade | 5 |
| Rosana | 21 anos | Login no app, ID Jovem, FGTS, CIN pela navegação | 4 |

**Indicadores obtidos** (opção 3 do menu):

| Indicador | Valor |
|---|---|
| Atendimentos | 12 |
| Resposta encontrada | 83,3 % |
| Taxa de acerto (ajudou) | 83,3 % |
| Tempo médio para encontrar | 25,7 s |
| Tentativas por atendimento | 1,17 |
| Facilidade de uso (1 a 5) | 4,3 |

**Dúvidas sem solução:**
- `como pedir seguro desemprego`
- `minha empresa nao pagou o fgts o que eu faço`

Os dois temas não estão na base. Ficam como próximas orientações a criar, depois de conferir as fontes oficiais.

**Dúvidas que precisaram de mais de uma tentativa:**
- `fiz 18 anos, preciso me apresentar no quartel?`: não encontrou nada na 1ª tentativa e só deu certo com `alistamento militar`.
- `baixei o app da carteira digital mas nao consigo entrar`: mostrou a Carteira de Trabalho Digital, que não resolvia. Com `nao consigo entrar na conta gov`, chegou na orientação 11.

**Melhoria feita a partir do teste:**
- A palavra `quartel` foi adicionada às palavras-chave da orientação 4 (Alistamento militar). Antes, a pergunta `fiz 18 anos, preciso me apresentar no quartel?` tinha **0 pontos**. Agora tem **3 pontos (confiança MÉDIA)** e é encontrada na primeira tentativa.

---

## Limitações

- A busca é por **palavras exatas** depois da normalização: não entende sinônimos que não estejam nas palavras-chave, erros de digitação (`titlo`) nem plural/singular diferentes (`documento` ≠ `documentos`).
- Não entende contexto nem negação: "não quero o CPF" pontua igual a "quero o CPF".
- Os prazos e regras mudam (ex.: calendário do título de eleitor em ano de eleição). A base precisa ser revisada periodicamente, e por isso cada orientação guarda a data de verificação.
- A detecção de dados pessoais é por regra (8+ dígitos ou `@`): não detecta um nome digitado, e pode recusar perguntas legítimas com números longos.
- Funciona só no terminal e só em português.

---

## Vídeo técnico

Link (YouTube, não listado): **_(https://youtu.be/5pEBoKCdeJM)_**