# Como usar o 8020-DS 4.0

Antes de abrir qualquer arquivo, duas decisões: o formato da peça e o template de partida. As duas saem de perguntas sobre como o trabalho vai chegar em quem recebe, não sobre gosto visual.

Quem está convertendo uma peça da versão 3 lê antes o [guia de migração](MIGRACAO.md).

## O caminho até a peça certa

**Como a peça será consumida?** Quando ela é lida sem ninguém para apresentar (relatório que circula entre áreas, estudo que o cliente abre no próprio ritmo, longform encaminhado para leitura), o formato é o book. Quando ela é apresentada ao vivo, ou enviada como apresentação para alguém percorrer slide a slide, o formato é o deck.

**Qual é a natureza do deck?** A segunda pergunta vale só para quem chegou no deck. Argumento denso e encadeado, decisão a ser tomada, capítulos com prova e número a cada passo pedem o [deck padrão](templates/deck/padrao/CONTRATO.md). Conteúdo institucional, visão, cultura, reunião de abertura, com mais imagem e respiro do que argumento, pede o [deck editorial](templates/deck/editorial/CONTRATO.md).

Na dúvida entre os dois decks, o desempate é honesto: se o público vai discutir o conteúdo linha a linha e sair com uma decisão, é o padrão; se vai assistir, absorver a direção e sair com uma impressão, é o editorial.

| Sinal na demanda | Template |
|---|---|
| Pesquisa com dados, achados e recomendação, para o cliente ler quando puder | [Book padrão](templates/book/padrao/CONTRATO.md) |
| Plano, estratégia ou diagnóstico que vai a uma sala para ser decidido | [Deck padrão](templates/deck/padrao/CONTRATO.md) |
| Abertura de relação, apresentação institucional, cultura, visão de marca | [Deck editorial](templates/deck/editorial/CONTRATO.md) |
| O mesmo trabalho precisa circular e também ser apresentado | Os dois, book e deck |

Na peça dupla, o book carrega o argumento completo, com a prova e as fontes, e o deck vira o guia da apresentação ao vivo, mais curto e com uma ideia por slide. O vocabulário é o mesmo nos dois: o que muda é a densidade, nunca o nome das coisas. Alteração em um obriga a conferência do outro.

## Da pasta copiada à peça entregue

1. **Copiar a pasta inteira do template**, não só o arquivo HTML. O book leva o hub mais a pasta `partes/`; os decks levam o `CONTRATO.md`.
2. **Ler o `CONTRATO.md` do template e as [regras](RULES.md).** O contrato traz a gramática dos tipos de slide ou de seção e o checklist de saída; as regras 18 a 27 regem todo texto visível.
3. **Ajustar os caminhos de `tokens/` e `assets/`** para a pasta nova. É onde o erro costuma aparecer, porque o book tem dois níveis, um para o hub e outro para as partes. No deck, preencher `data-marca`, `data-peca` e `data-canal`; no book, o `data-book` de cada página.
4. **Escrever e montar dentro das camadas.** Base clara sempre; o laranja e o escuro entram como momentos, no máximo um de página inteira por capítulo e nunca em dois seguidos. Gráfico e diagrama em SVG real, componente copiado do catálogo em `patterns/` em vez de inventado.
5. **Rodar as duas passadas do verificador** e fechar pelo checklist do contrato, com o PDF gerado por Chrome headless e lido página a página.

```bash
python3 verificar.py caminho/da/peca.html
```

Durante a montagem, quando o sumário, as separatrizes e o recap ainda não existem, `--fragmento` transforma essas cinco checagens de contrato em aviso e mantém todo o resto como erro. Na entrega, roda-se sem ele.

A segunda passada é a geometria, que só a renderização mostra. O Playwright não abre `file://`, então a peça precisa de um servidor local; em `verificar-geometria.js` trocam-se `__URL__` e `__DIR__` e o arquivo inteiro vai para o Playwright. Zero erro nas duas é a condição de saída.

## A receita de cada tipo de slide

O registro sai do papel do slide na narrativa, não do gosto. Os limites são de caracteres com espaço, e passar do limite não deixa a linha menor: o slide corta ou o texto sobrepõe. Todo slide leva a nota do apresentador em `<aside class="notas">`, até 300 caracteres.

| Tipo | Registro | O que cabe |
|---|---|---|
| Capa | faixa laranja | título até 48 com o último termo em `<em>`, frase central até 110, data; foto 16 por 9 ao lado |
| Sumário | quieto | título até 60 e uma linha por capítulo, com o nome e a página |
| Separatriz | faixa laranja | `Capítulo N` mais nome até 30, título até 48, frase até 110, numeral grande e a lista das seções |
| Texto em duas colunas | faixa | duas colunas de prosa curta, cada uma com um parágrafo de abertura e até quatro linhas |
| Comparação | faixa | duas colunas, `Hoje` e `Com o plano`, até cinco itens de uma linha em cada |
| Números em linha | faixa | até três números, cada um com a frase que diz o que se mede e por que importa |
| Barras com ênfase | faixa | até oito barras, valor escrito na marca, o 20 em laranja, fonte ao pé |
| Pareto | faixa | uma série de barras e a linha acumulada no mesmo eixo, com o corte marcado |
| Matriz dois por dois | faixa | dois eixos nomeados e até oito pontos rotulados |
| Perfis | faixa | até três perfis com retrato 4 por 5, nome, papel e uma frase |
| Mapa de atores | faixa | três anéis, decide, influencia e observa, com até cinco nomes por anel |
| Veículos em três colunas | faixa | três colunas com o meio e a cidade, até seis linhas por coluna |
| Lista-razão | faixa | até cinco itens numerados, título até 50 e descrição até 110 |
| Passos da pauta | faixa | até seis passos, um verbo por passo |
| Próximos passos | faixa | tabela de até cinco linhas e quatro colunas, célula até 40 |
| KPI com meta | faixa | até três metas, cada uma com valor de hoje, meta e prazo |
| Equipe | faixa | até seis pessoas com miniatura 1 por 1, nome e papel |
| Tabela no topo | topo | até seis colunas e seis linhas a 15 px, célula até 40 |
| Fases | topo | até quatro fases, marcadas como feita, atual ou futura, com o quando |
| Fluxo | topo | até cinco caixas com seta por marcador, uma linha de descrição por caixa |
| Orçamento | topo | até seis linhas com a barra dentro da célula e o total |
| Esquema de fechamento | topo | tese no topo, até três desdobramentos e o acordo na base, conectores anotados |
| Recap | quieto | `O que aprendemos no capítulo N` e três achados escritos por inteiro, com o método |
| Aparte, citação | cheio, escuro | citação até 120 e a atribuição |
| Mensagem-mãe | cheio, laranja | statement até 70, com o núcleo em `<strong>` |
| Respiro em foto | cheio, escuro | foto 16 por 9 de sangria, véu na base e statement até 70 |
| Foto com legenda | faixa | foto 3 por 2 ao lado de dois parágrafos curtos, legenda até 120 |
| Contracapa | cheio, escuro | nome, cliente, data, a logo e os três endereços |

Toda faixa carrega as três coisas da regra 38: capítulo, título descritivo e frase central. O achado mora na frase, nunca no título.

## A receita de cada seção do book

| Seção | O que cabe |
|---|---|
| Hub | tipo de peça e data, título com a assinatura em `<em>`, o mapa das partes com tempo de leitura por capítulo, o bloco "continuar de onde parou" e a foto de abertura em 21 por 9 |
| Abertura de parte | numeral grande, título da parte, frase com o núcleo em `<strong>`, os tempos dos capítulos na margem |
| Cabeça de capítulo | número e tempo, título, e na margem o que o capítulo prova em uma frase |
| Prosa com notas | parágrafos de 17 px na medida de leitura; a nota vai para a margem, ao lado do parágrafo que a chama |
| Figura | imagem 16 por 9, ou 3 por 2 ao lado do texto; a legenda vai para a margem quando a figura ocupa a coluna |
| Figura com dado | cabeça com título e sub, o SVG com papel e rótulo, a leitura em palavras e o livro-razão em `details` com a fonte |
| Scrollytelling | a figura fica presa na coluna e os passos são notas curtas na margem; cada passo traz `data-estado` e `data-leitura` |
| Fichas | uma por público, retrato 4 por 5, nome, papel, uma frase e três campos |
| Momento | um por parte, no máximo: statement com o núcleo em `<strong>` |
| Recap | `O que a parte N mostrou`, três achados por inteiro e o método |
| Navega | anterior e próximo como filete; a última parte volta ao início |

## O catálogo

Nove páginas com os blocos ao vivo e o código para copiar. Fundamentos primeiro, depois o conteúdo, depois os dois formatos.

- [patterns/tipografia.html](patterns/tipografia.html): a escala com salto, a assinatura em itálico, o rótulo em caixa baixa, os tamanhos do slide
- [patterns/cores.html](patterns/cores.html): os seis primitivos, os papéis, os momentos, os quatro papéis do laranja e a matriz de contraste medida ao vivo
- [patterns/layouts.html](patterns/layouts.html): a grade 80/20, a escala de espaço, os pontos de quebra, os cinco registros do slide, a impressão
- [patterns/estados.html](patterns/estados.html): o filete vivo, os três níveis de ação, campos, seleção, navegação, retorno, tabela, o quadrado de 8 px e o foco
- [patterns/dado.html](patterns/dado.html): vinte formas em SVG para copiar, as dezoito regras e o validador de paleta
- [patterns/diagramas.html](patterns/diagramas.html): fluxo, mapa de atores, esquema e matriz, em ângulo reto e com seta por marcador
- [patterns/imagens.html](patterns/imagens.html): a política de imagem, os quatro formatos, o prompt base do gerador e as onze cenas
- [patterns/deck.html](patterns/deck.html): os cinco registros, os tipos de slide, o visualizador e os limites de texto
- [patterns/book.html](patterns/book.html): o hub, a margem viva, as notas, o scrollytelling, as fichas e o recap

## Impressão

Deck e book imprimem do mesmo arquivo, pelo Chrome headless. O deck pagina um slide por página em 1280 por 720; o book quebra página antes de cada capítulo e vira duas colunas, quatro de conteúdo para uma de margem.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="deck.pdf" --print-to-pdf-no-header \
  "http://localhost:PORTA/caminho/deck.html"
```

O PDF se lê página a página antes de sair: o que passa na tela passa no papel, e o contrário também.
