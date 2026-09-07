# Deck editorial, contrato de uso

Template do 8020-DS 4.0 para peça institucional em slide. O exemplo pronto é `deck.html`, a "Visão 2027 da Casa do Campo": 17 slides, três capítulos, universo fictício. Quem copia a pasta troca o conteúdo e mantém a gramática.

## Quando usar

Peça institucional: visão de empresa, cultura de trabalho, abertura de relação com um cliente, reunião de abertura com direção e lideranças. O deck editorial carrega pouco dado e muito texto, foto e respiro; o ritmo é de leitura em voz alta, um argumento por slide.

Se a peça é densa de dado ou de decisão (diagnóstico, plano de canais, orçamento, board), use o deck padrão em `../padrao/`. Os dois partem das mesmas camadas e podem trocar slides entre si; a diferença está no que cada um faz de exemplo.

## Gramática

Cada slide é um filho direto de `.deck`, com um comentário `<!-- NN · tipo -->` antes e um `<aside class="notas">` no fim, com a nota do apresentador. O autor não escreve contador nem trilho: o `deck.js` escreve.

| Tipo | O que o autor escreve | O que o deck.js escreve |
|---|---|---|
| Capa | `.slide.s-faixa` com `.faixa.laranja` (`.cap` com a logo, `h2` com o último termo em `<em>`, `p.frase` com o núcleo em `<strong>`, `.pe > .contador > span.quando` com a data) e `.foto-area` (`img` com `alt` e um `span` de legenda) | o "01 de N" ao lado da data e o trilho |
| Abertura editorial | `.slide.s-faixa` com `.faixa` (`.cap`, `h2`, `p.frase`) e `.conteudo` com `.foto-legenda` (um `div` com `img` e `p.legenda`, outro com dois `p.texto`) e `p.fonte` | `.pe` inteiro: contador e trilho |
| Sumário | `.slide.s-quieto` com `.conteudo` (`h2`, `ol.sumario-slide` com `li > span.n, span, span.pg`) e `.cromo > .capitulo` com `small` | a linha vertical e o contador do `.cromo` |
| Separatriz | `.slide.s-faixa` com `.faixa.laranja` (`.cap` com `<b>Capítulo N</b> de 3`, `h2`, `p.frase`) e `.conteudo.separatriz` (`.separatriz-numeral`, `ol.separatriz-lista` com `li > span.n, span`) | contador e trilho |
| Citação com dado | `.slide.s-faixa` com `.conteudo` (`.pilha` com `p.citacao` e `p.atrib`, `.numeros > p` com o número em `<strong>`, `p.fonte`) | contador e trilho |
| Fluxo | `.slide.s-topo` com `.faixa` (`.cabeca` com `.cap` e `h2`; `p.frase`) e `.conteudo` com `.grafico.fluxo > svg` (viewBox 1088 por 240, caixas de 196 px, seta por `<marker>` em `<defs>`, `role="img"`, `aria-label`, `<title>`) e `p.fonte` | `.pe` com contador e trilho, na base da faixa |
| Respiro em foto, foto de seção | `.slide.s-cheio.tema-escuro.com-foto` com `.foto-cheia > img`, `.veu` e `.sobre` (`p.statement` com o núcleo em `<strong>`, `.rodape-slide > span` com o capítulo); `aside.notas` fora do `.sobre` | o `span.tab` com o contador no rodapé |
| Recap de capítulo | `.slide.s-quieto` com `.conteudo` (`h2`, `ol.recap` com `li > strong` mais uma frase, `p.fonte` com o método) e `.cromo > .capitulo` | linha vertical e contador |
| Compromissos | `.slide.s-faixa` com `.conteudo` com `ol.lista-razao` (`li > span.n` e `div > b, span`) e `p.fonte` | contador e trilho |
| Fases | `.slide.s-topo` com `.conteudo` com `.fases > .fase.feita`, `.fase.atual`, `.fase.futura` (`span.quando`, `b`, texto) e `p.fonte` | contador, trilho e a cascata das linhas |
| Fechamento em esquema | `.slide.s-topo` com `.conteudo` com `.grafico.esquema > svg` (viewBox 1088 por 380: tese em caixa cheia, três desdobramentos, acordo com contorno laranja, "desdobra em" e "sustentado por") | contador e trilho |
| Contracapa | `.slide.s-cheio.tema-escuro` com `.pilha` (`p.fonte` com nome, cliente e data; `p.statement` a 40 px; `.enderecos` com três `div > b`) e `.rodape-slide > span > img` da logo | o contador no rodapé |

O `deck.js` também monta a moldura em chumbo, o topo com marca, peça e capítulo atual, as miniaturas, a lista de atalhos e a visão do apresentador. O nome do capítulo no topo sai do `.cap` da faixa, do `.capitulo` do cromo ou do primeiro `span` do rodapé; a capa e a contracapa, que só têm a logo, aparecem como "Capa" e "Contracapa".

## Esqueleto do exemplo

| Slide | Tipo | Registro | Capítulo |
|---|---|---|---|
| 01 | Capa | `.s-faixa` com `.faixa.laranja` e `.foto-area` | |
| 02 | Abertura editorial | `.s-faixa`, faixa em tinta | Abertura |
| 03 | Sumário | `.s-quieto` | Sumário |
| 04 | Separatriz | `.s-faixa` com `.faixa.laranja` | Capítulo 1, Visão |
| 05 | Citação com dado | `.s-faixa` | Capítulo 1, Visão |
| 06 | Fluxo | `.s-topo` | Capítulo 1, Visão |
| 07 | Respiro em foto | `.s-cheio.tema-escuro.com-foto` | Capítulo 1, Visão |
| 08 | Recap | `.s-quieto` | Capítulo 1, Visão |
| 09 | Separatriz | `.s-faixa` com `.faixa.laranja` | Capítulo 2, Cultura |
| 10 | Compromissos | `.s-faixa` | Capítulo 2, Cultura |
| 11 | Foto de seção | `.s-cheio.tema-escuro.com-foto` | Capítulo 2, Cultura |
| 12 | Recap | `.s-quieto` | Capítulo 2, Cultura |
| 13 | Separatriz | `.s-faixa` com `.faixa.laranja` | Capítulo 3, Caminho |
| 14 | Fases | `.s-topo` | Capítulo 3, Caminho |
| 15 | Recap | `.s-quieto` | Capítulo 3, Caminho |
| 16 | Fechamento em esquema | `.s-topo` | Fechamento |
| 17 | Contracapa | `.s-cheio.tema-escuro` | |

## Momentos e tetos

O laranja tem quatro papéis: momento (`.faixa.laranja`, `.tema-laranja`), ação primária dentro do momento, estado atual (o quadrado de 8 px) e o 20 do dado. O laranja funcional e o 20 do dado não contam no teto.

- No máximo três momentos de acento por slide.
- Momento de página inteira (`.s-cheio` com tema): um por capítulo, nunca em dois slides seguidos. No exemplo, o slide 07 é o do capítulo 1 e o slide 11 é o do capítulo 2; o capítulo 3 não tem. A contracapa vem depois do esquema, que não é momento.
- Faixa laranja: a capa e uma separatriz por capítulo. No exemplo são quatro: slides 01, 04, 09 e 13.
- Branco sobre laranja só a partir de 24 px, ou 19 px em peso 700. O texto pequeno dentro do momento laranja fica preto pelos papéis da camada; não sobrescrever.
- Todo slide de capítulo leva `.cap` com `<b>Capítulo N</b> Nome`, até 30 caracteres somados.

## Visualizador e teclado

O `deck.js` monta a moldura e responde ao teclado:

| Tecla | Faz |
|---|---|
| seta para a direita, seta para baixo, espaço, PageDown | próximo slide |
| seta para a esquerda, seta para cima, PageUp | slide anterior |
| Home, End | primeiro e último |
| o | abre e fecha as miniaturas de todos os slides, com a lista de capítulos na margem |
| f | tela cheia |
| p | visão do apresentador em janela própria, sincronizada com a janela do deck |
| ? | abre e fecha a lista de atalhos |
| t | zera o tempo decorrido, na visão do apresentador |
| Esc | fecha miniaturas e atalhos |

Os botões da base fazem o mesmo: `o`, `f`, `p`, `?`, Anterior e Próximo. A visão do apresentador abre em `deck.html?apresentador=1` e mostra o slide atual, as notas, o tempo decorrido e o próximo slide; as duas janelas andam juntas. O endereço guarda o slide: `deck.html#12` abre no 12, e o `#` acompanha a navegação. Sem JavaScript os slides empilham na vertical e continuam legíveis.

## Limites de texto

Medidos em caracteres, com espaço. Passou do limite, o slide corta ou o texto sobrepõe.

| Onde | Teto |
|---|---|
| Título da faixa (`h2`) | 48 |
| Frase central (`.frase`) | 110 |
| Título de slide quieto (`.s-quieto h2`) | 60 |
| Statement (`.statement`) | 70 |
| Citação (`.citacao`) | 120 |
| Item de lista: título (`b`) e descrição (`span`) | 50 e 110 |
| Célula de tabela | 40, e no máximo seis colunas no registro topo |
| Legenda de foto | 120 |
| Nota do apresentador (`.notas`) | 300 |
| Capítulo mais rótulo (`.cap`) | 30 |

No registro topo a faixa tem 240 px fixos e o conteúdo tem 392 px úteis; título de até duas linhas a 36 px; tabela de até seis linhas a 15 px. Nenhum texto do slide fica abaixo de 14 px efetivos (texto de SVG multiplicado pela escala do viewBox). Nada sai dos 1280 por 720.

## Imagens

As imagens moram em `../../../assets/imagens/`, cada uma em dois arquivos: o grande (1600 px de largura ou 1000 px de altura) e o `-min.jpg` de 640 px, para miniatura e lista. Quatro proporções, uma por uso:

- 16 por 9: a foto da capa em `.foto-area`, a foto cheia em `.foto-cheia` e o respiro. 1600 px de largura.
- 3 por 2: a foto ao lado do texto em `.foto-legenda`; o CSS corta o 16 por 9.
- 4 por 5: o retrato de ficha e de perfil. 1000 px de altura.
- 1 por 1: a miniatura de perfil de 72 px em `.perfil .foto` e `.pessoa .foto`, no deck padrão, cortada do 4 por 5 ao centro.

Toda `img` leva `alt` descritivo, ou `alt=""` quando é decorativa ao lado do nome. Toda imagem gerada é marcada na legenda ou na fonte: "Imagem ilustrativa gerada para o exemplo". Foto de página inteira leva o `.veu` para o texto ficar legível.

## Impressão

O mesmo arquivo imprime um slide por página em 1280 por 720, sem moldura, sem notas e sem animação; o laranja do dado vira hachura. Pelo Chrome headless:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=deck.pdf --print-to-pdf-no-header "file:///caminho/deck.html"
```

Conferir o PDF página a página antes de enviar: o que passa na tela passa no papel, e o contrário também.

## Checklist de saída

- [ ] Copiou a pasta inteira e substituiu todo o conteúdo fictício: textos, nomes, números, notas e imagens.
- [ ] Os caminhos de tokens e assets apontam para `../../../tokens/` e `../../../assets/`, ou para onde a cópia mora.
- [ ] Toda faixa tem título descritivo e frase central com o núcleo em `<strong>`; o achado está na frase, não no título.
- [ ] Todo capítulo tem separatriz laranja e recap com os achados por inteiro e a fonte do método.
- [ ] O esquema fecha a peça antes da contracapa; capa e contracapa dizem nome, cliente, data e o que a peça contém.
- [ ] Os momentos estão no teto: um de página inteira por capítulo, nunca dois seguidos, até três acentos por slide.
- [ ] Acentuação correta em tudo, inclusive em caixa alta, `alt`, `aria-label` e comentários.
- [ ] Toda imagem tem `alt` e, se foi gerada, a marcação na legenda ou na fonte.
- [ ] O PDF foi gerado e lido página a página.
- [ ] O verificador geométrico rodou nos 17 slides sem corte, sem sobreposição e com a menor fonte em 14 px ou mais.
