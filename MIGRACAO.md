# Da versão 3 para a 4

O núcleo de marca não muda: paleta fechada, momentos com teto, Montserrat única, ângulo reto, sem sombra, contrato didático do deck. Muda a moldura, e ela muda inteira. O que a 4.1 ajustou sobre a 4.0 está no fim deste guia.

Este guia diz o que quebra numa peça da versão 3, o que se converte por regra e o que exige decisão de quem migra.

## A primeira decisão: converter ou não converter

Peça entregue e aprovada não se migra. Ela continua abrindo no navegador, porque carrega os próprios `tokens/` e `assets/` da versão 3, e reabri-la para trocar a moldura só cria risco de estragar o que o cliente já leu.

Migra-se quando a peça vai ganhar uma versão nova, quando ela vira template interno, ou quando o cliente pediu continuidade visual com o trabalho novo. Nesse caso o caminho é um só: **começar do template da 4.0 e trazer o conteúdo, não abrir a peça antiga e trocar as classes.**

O motivo é mecânico. A camada de layout foi reescrita: o `deck.css` da versão 3 tem 42 classes com prefixo `s-` e o `book.css` tem 68 com prefixo `b-`, e quase nenhuma sobrevive com o mesmo nome. Uma busca e substituição deixa a peça meio convertida, que é pior do que as duas pontas.

## O que se converte por regra

**Tokens de tipografia.** A escala trocou de `--fs-*` por `--t-*`, com salto de 1,25 e display até 96 px.

| Versão 3 | Versão 4 |
|---|---|
| `--fs-micro` | `--t-micro`, 11,5 px |
| `--fs-small` | `--t-small`, 13 px |
| `--fs-body` | `--t-body`, 15 px |
| `--fs-lead` | `--t-lead`, 18 px |
| `--fs-h2` | `--t-h2`, 28 px |
| `--fs-title` | `--t-title`, 36 px |
| `--fs-statement` | `--t-statement`, 48 px |
| `--fs-display` | `--t-display`, até 96 px |
| `--font-body`, `--font-display`, `--font-data` | `--font`, uma só |
| `--w-body`, `--w-medium`, `--w-label`, `--w-title`, `--w-black` | `--w-corpo`, `--w-medio`, `--w-rotulo`, `--w-titulo`, `--w-display`, mais `--w-fino` (300) |
| `--line` | `--rule`; o filete de abertura é `--rule-strong` |
| `--ease` | `--ease-out`, com `--dur-fast`, `--dur` e `--dur-slow` |

**Tokens que saíram e não têm substituto.** `--radius`, `--radius-sm`, `--radius-lg` e `--radius-pill` viram `--r-0`, que é zero; `--r-media` de 6 px existe só para mídia de book. `--grad-quente` e `--grad-fundo` saíram com o gradiente (regra 4). `--tracking-eyebrow` e `--tracking-label` saíram com o olho de seção em caixa alta. `--surface-ink` virou `--floor` com `--floor-ink`.

**Tokens novos que a peça precisa conhecer.** `--ink-soft` e `--meta` para os dois níveis de texto secundário; `--dado-1` a `--dado-4` e `--dado-0` para a rampa; `--s-1` a `--s-10` para o espaço; `--measure`, `--max-prose` e `--gutter` para a medida de leitura; `--registro` para o deslocamento do botão; `--sl-w` e `--sl-h` para o slide.

**Contraste.** Os cinzas de texto subiram para passar o AA no tamanho em que são usados: `--meta` de 50 para 60 por cento, `--muted` de 58 para 66, `--rule-strong` de 34 para 50. Peça que copiava os valores antigos à mão fica abaixo do mínimo e precisa passar a consumir os papéis.

## O que muda de forma e exige reescrita

| O que a peça de 3 tem | O que a 4.0 põe no lugar |
|---|---|
| Cartão com borda, raio e sombra em toda seção | Filete de 1 px como separador. Cartão só para coleção de itens iguais, sem borda e sem raio (regra 31) |
| Olho de seção em caixa alta com espacejamento (`s-eyebrow`, `b-eyebrow`) | Rótulo em caixa baixa a 13 px, peso 600, uma vez por capítulo |
| Barra lateral colorida, caixa de ícone, pílula, cápsula | Nada disso. O único ícone é o quadrado de 8 px em quatro preenchimentos (regra 36) |
| Deslocamento do bloco ao passar o ponteiro | Filete que conta o estado, e registro no botão primário (regras 32 e 34) |
| Estado só por cor | Estado com forma ou com a palavra: enviar, enviando, enviado às 14:32 (regra 35) |
| Slide de título centralizado, texto solto no meio | Cinco registros escolhidos pelo papel do slide, com faixa de um terço (regra 37) |
| Autor numerando o slide à mão | O `deck.js` escreve contador e trilho; o autor escreve só os slides (regra 39) |
| `deck-print.html` separado | O mesmo arquivo imprime, um slide por página (regra 40) |
| Grade de cartões no hub do book | O hub é um mapa: partes e capítulos numerados de 1 a N, sem tempo de leitura e sem "continuar de onde parou" |
| Nota de rodapé no fim da página | Nota na margem, ao lado do parágrafo que a chama |
| Dica flutuante no gráfico | Leitura em palavras, visível em repouso, com o livro-razão embaixo (regra 42) |
| Série de dado em duas ou três cores | Uma tonalidade em quatro degraus; o laranja é o 20, um por gráfico (regra 41) |
| Gradiente de marca como superfície | Superfície chapada: papel, areia, chumbo, laranja (regra 4) |
| Imagem com raio e borda fina | Retângulo reto, sem raio e sem borda; véu na base quando o texto entra por cima (regra 3) |

## O que exige decisão de quem migra

Três coisas o sistema não decide sozinho, porque dependem do argumento da peça.

**1. Qual registro cada slide recebe.** Na versão 3 o slide era um contêiner livre; na 4.0 o registro vem do papel do slide na narrativa. Slide de evidência vai para a faixa à esquerda; tabela larga, fases, fluxo e esquema vão para a faixa no topo; sumário, recap e transição vão para o quieto; aparte, respiro e mensagem-mãe viram momento de página inteira. Escolher errado cabe, mas a peça perde o ritmo.

**2. Qual é a frase central de cada slide.** A faixa exige título descritivo mais frase central (regra 38), e muita peça da versão 3 tem só o título, com o achado dentro dele. Migrar quer dizer separar as duas coisas: o título diz do que o slide trata, a frase diz o que ele prova. Onde não houver frase, ela precisa ser escrita, e escrever a frase costuma revelar o slide que não tinha tese.

**3. Onde ficam os momentos.** O teto é um momento de página inteira por capítulo, nunca dois seguidos, e uma faixa laranja de separatriz por capítulo (regra 6a). Peça da versão 3 que usava o escuro ou o laranja com liberdade precisa escolher quais momentos ficam. Escolher é do autor; o verificador só conta.

## O caminho, passo a passo

1. Copiar a pasta do template da 4.0 que corresponde ao formato da peça antiga.
2. Preencher `data-marca`, `data-peca` e `data-canal` no deck, ou `data-book` em cada página do book.
3. Passar o conteúdo slide a slide, ou capítulo a capítulo, escolhendo o registro e escrevendo a frase central de cada faixa.
4. Trazer os gráficos como SVG, trocando a paleta pelas classes `d1` a `d4` e `o20`, e acrescentando a leitura em palavras e o livro-razão.
5. Trazer as imagens para `assets/imagens/`, em dois arquivos por imagem, com `alt` descritivo e a marcação de ilustrativa quando forem geradas.
6. Rodar `python3 verificar.py` na peça nova e o `verificar-geometria.js` no Playwright. Zero erro nas duas.
7. Gerar o PDF pelo Chrome headless e ler página a página.

## O que não muda

Vale repetir, porque na hora da migração dá vontade de mexer: a paleta continua fechada nas mesmas seis cores, a logo continua sem recoloração, Montserrat continua sendo a única família, o ângulo reto continua, e as regras editoriais de 18 a 27 continuam idênticas. Texto aprovado na versão 3 passa na 4.0 sem uma vírgula de diferença; na 4.1, só o itálico de título e os metadados saem.

## Da 4.0 para a 4.1

A 4.1, de outubro de 2026, alinha o sistema ao que os decks e books reais pediram depois da 4.0. Nenhuma regra mudou de número; as novas entram com letra.

| Mudou | Na 4.0 | Na 4.1 |
|---|---|---|
| Modos de trabalho | As regras valiam inteiras em toda peça | Expresso (o template inteiro) ou sob medida (logo, cor, fonte e o núcleo das regras, com a composição livre) |
| Substrato | Papel claro em toda peça | Papel claro por padrão; a noite (`body.noite`) para book e página lidos na tela; impressão sempre no papel |
| Itálico | Assinatura em `<em>` no título de capa, hero e abertura | Sem itálico em título, statement e frase; o destaque é peso |
| Peso de display | 800, e 900 no itálico | Até 700 (regra 5a) |
| Recap | Obrigatório em todo capítulo do deck e em toda parte do book | Só em capítulo longo, de oito slides ou mais (regra 28); os templates não têm |
| Deck | Título a 36 e 40 px, corpo a 19 px | Título a 28 px, corpo a 15 px, um assunto por slide; o filete entre as partes fica (regra 16a) |
| Visual | Gráfico ou dispositivo em toda declaração massiva | Dispositivo visual em todo slide de evidência e capítulo, animado para ser lido, com a direção partindo de referência concreta (15a a 15c) |
| Book | Tempo de leitura e "continuar de onde parou" guardado no navegador | Nada guardado e nenhum tempo de leitura (22a); capítulos numerados de 1 a N também entre partes |
| Bastidor | "Como ler", "O que o capítulo prova", "Base:" e o método no recap | Fora: a peça fala do assunto, não de si (22 e 22a) |
| Título | Descritivo, sem o achado | Descritivo e com informação: nunca uma palavra genérica como "Contexto" (21) |
| Capa | Frase central da faixa onde mora o achado | Frase descritiva na capa e na separatriz; o achado principal fica no capítulo que o constrói (38) |
| Status de execução | Não existia | Verde e amarelo, a única cor fora da paleta, com a palavra junto (6c) |
| PDF | Gerado a cada entrega, por comando solto | Sob demanda, pelo `imprimir.py`, que confere páginas, tamanho e fonte |
| Verificação | Em 1440, 900 e 600 sempre | Nas larguras em que a peça vai ser lida; nenhum gráfico rola na largura de leitura (47a, 50) |

Peça montada na 4.0 continua abrindo com os próprios arquivos. Para levar uma peça da 4.0 à 4.1: trocar `tokens/` e `assets/` pelos da 4.1, tirar o `<em>` dos títulos, tirar os recaps de capítulo curto, tirar o bloco de continuar e os tempos do book, renumerar os capítulos de 1 a N e rodar o verificador, que aponta o resto.

