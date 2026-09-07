# Contrato, deck padrão (8020-DS 4.0)

## Quando usar
Peça densa, didática e sequencial: plano, diagnóstico, estratégia com capítulos, prova e número a cada passo, decisão a ser tomada numa sala. Se a peça é institucional, de visão ou de abertura de relação, com mais imagem e respiro do que argumento encadeado, use o deck editorial (`templates/deck/editorial/`).

## Gramática
O deck é o elemento `.deck`, com os slides como filhos diretos. O autor escreve o slide; o `deck.js` monta a moldura do visualizador, escreve o contador e o trilho de cada slide, abre as miniaturas, os atalhos e a visão do apresentador. Sem JavaScript os slides empilham e continuam legíveis.

Cinco registros, escolhidos pelo papel do slide na narrativa:

- `.slide.s-faixa`: faixa de tinta à esquerda (um terço) com `.faixa` e o conteúdo em `.conteudo`. É o padrão de todo slide de evidência: texto, lista, gráfico, comparação, perfis, atores, passos, números, próximos passos.
- `.slide.s-topo`: faixa de 240 px no topo, para conteúdo largo: tabela de muitas colunas, fases, fluxo, esquema. O conteúdo tem 392 px úteis.
- `.slide.s-quieto`: a margem 80/20, com `.conteudo` e `.cromo`. Sumário, recap de capítulo, transições.
- `.slide.s-cheio` com `.tema-laranja` ou `.tema-escuro`: os momentos. Mensagem-mãe em laranja; aparte, foto de respiro (`.com-foto`, com `.foto-cheia`, `.veu` e `.sobre`) e contracapa em escuro.
- `.faixa.laranja` dentro de `.s-faixa`: a abertura de capítulo e a capa. Uma por capítulo, nunca em dois slides seguidos.

A faixa carrega: `.cap` (`<b>Capítulo N</b> Nome`, até 30 caracteres), `h2` (título descritivo, até 48 caracteres, nunca o achado), `.frase` (a frase central, obrigatória, até 110 caracteres, com o núcleo em `<strong>`) e o `.pe`, que o sistema escreve. Na capa o `.pe` pode trazer `<span class="quando">` com a data; o contador entra ao lado. Na capa o último termo do título vai em `<em>`: é a assinatura da marca.

Blocos de conteúdo (todos em `deck.css` e `regua.css`): `.duas-colunas`, `.comparacao` (`.hoje` e `.depois`), `.numeros`, `.grafico` (SVG real com `role="img"`, `aria-label` e `<title>`), `.matriz`, `.citacao` com `.atrib`, `.recap`, `.statement`, `.perfis` com `.perfil`, `.atores-mapa`, `.fases` com `.fase` (`feita`, `atual`, `futura`), `.tabela` (`.proximos`, `.orcamento`), `.sumario-slide`, `.separatriz` com `.separatriz-numeral` e `.separatriz-lista`, `.foto-area`, `.foto-legenda`, `.lista-razao`, `.metas`, `.equipe`, `.esquema`, `.enderecos`. Cada slide leva um `<aside class="notas">` com a nota do apresentador (até 300 caracteres), invisível no deck e lida na visão do apresentador.

## Esqueleto do exemplo
Vinte e dois slides, três capítulos. Todo capítulo abre com separatriz e fecha com "O que aprendemos no capítulo N" (regra 28); o deck fecha com o esquema (regra 29) e a contracapa descritiva.

| Slide | Tipo | Registro | Capítulo |
|---|---|---|---|
| 01 | capa descritiva com foto | faixa laranja | |
| 02 | sumário | quieto | |
| 03 | separatriz | faixa laranja | 1, Leitura do desafio |
| 04 | texto em duas colunas | faixa | 1 |
| 05 | comparação hoje e com o plano | faixa | 1 |
| 06 | recap | quieto | 1 |
| 07 | separatriz | faixa laranja | 2, Diagnóstico |
| 08 | números em linha | faixa | 2 |
| 09 | barras com o 20 em laranja | faixa | 2 |
| 10 | Pareto | faixa | 2 |
| 11 | matriz dois por dois | faixa | 2 |
| 12 | aparte, citação | cheio, escuro | 2 |
| 13 | recap | quieto | 2 |
| 14 | separatriz | faixa laranja | 3, Públicos e plano |
| 15 | perfis com retrato | faixa | 3 |
| 16 | mapa de atores | faixa | 3 |
| 17 | mensagem-mãe | cheio, laranja | 3 |
| 18 | fases | topo | 3 |
| 19 | próximos passos | faixa | 3 |
| 20 | recap | quieto | 3 |
| 21 | esquema de fechamento | topo | Fechamento |
| 22 | contracapa com os endereços | cheio, escuro | |

## Momentos e tetos
Momento de página inteira (`.s-cheio` com tema): no máximo um por capítulo, nunca em dois slides seguidos. No exemplo, o aparte escuro no 12 e a mensagem-mãe laranja no 17. A faixa laranja de separatriz é uma por capítulo. O laranja dentro do conteúdo é o 20 do dado (um por gráfico) e o quadrado de estado; nada mais. Branco sobre laranja só a partir de 24 px; o texto pequeno da faixa laranja é preto, e a camada já resolve isso.

## Visualizador e teclado
O `deck.js` monta a moldura em chumbo com a marca (`data-marca`), a peça (`data-peca`), o capítulo e o título do slide atual no topo; o contador, as teclas, anterior e próximo e o trilho de progresso na base. O endereço guarda o slide (`#12`). `data-canal` nomeia o canal que sincroniza as janelas.

| Tecla | Faz |
|---|---|
| seta para a direita, seta para baixo, espaço, PageDown | próximo slide |
| seta para a esquerda, seta para cima, PageUp | slide anterior |
| Home e End | primeiro e último |
| o | miniaturas de todos os slides, com a lista de capítulos na margem |
| f | tela cheia |
| p | visão do apresentador em janela própria (`?apresentador=1`), sincronizada |
| t | zera o tempo, na visão do apresentador |
| ? | abre e fecha a lista de atalhos |
| Esc | fecha |

A visão do apresentador mostra o slide atual, as notas, o tempo decorrido, o contador e o próximo slide. As duas janelas ficam no mesmo slide; avança-se de qualquer uma.

## Limites de texto
Título da faixa 48 caracteres; frase central 110; título de slide quieto 60; statement 70; citação 120; título de item de lista 50 e descrição 110; célula de tabela 40 e no máximo seis colunas na faixa do topo; legenda de foto 120; nota do apresentador 300; capítulo mais rótulo 30. Nada abaixo de 14 px efetivos. Nenhum elemento sai dos 1280 por 720; no registro topo, título de até duas linhas e tabela de até seis linhas a 15 px. O verificador mede caixa fora do slide, texto sobre texto, texto contra traço em SVG e a fonte mínima.

## Impressão
O mesmo arquivo imprime um slide por página (`@page` de 1280 por 720), com a faixa colorida, o contador no rodapé e o laranja do dado em hachura. Comando:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="deck.pdf" --print-to-pdf-no-header "file:///caminho/da/peca/deck.html"
```

## Checklist de saída
- [ ] Copiou a pasta inteira e substituiu todo o conteúdo fictício, inclusive as imagens e os endereços da contracapa?
- [ ] Caminhos de `tokens/` e `assets/` apontando para a peça nova? `data-marca`, `data-peca` e `data-canal` preenchidos?
- [ ] Toda faixa com título descritivo e frase central; capa e contracapa descritivas; sumário; separatriz e recap em todo capítulo; esquema de fechamento?
- [ ] Momentos dentro do teto; faixa laranja uma por capítulo; nenhum laranja além do 20 do dado e do estado?
- [ ] Acentuação conferida em caixa alta e nos `alt`; sem travessão; nada abaixo de 14 px?
- [ ] Toda imagem com `alt` descritivo e, se gerada, marcada como ilustrativa?
- [ ] Verificador geométrico sem corte, sem sobreposição e sem texto contra traço?
- [ ] PDF gerado pelo Chrome e lido página a página?
