# Contrato do book padrão

Template de book do 8020-DS 4.0. O exemplo é o "Plano de presença de marca no Cerrado", book de plataforma de comunicação para a Casa do Campo, julho de 2026: três partes, sete capítulos, 41 minutos de leitura. Conteúdo e imagens são fictícios.

## Quando usar

Peça longa de leitura assíncrona: plataforma de comunicação, relatório de território, diagnóstico extenso, qualquer material que o leitor percorre no próprio ritmo em vez de acompanhar uma apresentação. O book abre num hub (`index.html`) e se desdobra em partes (`partes/parte-N.html`), cada uma com dois ou três capítulos, um recap e a navegação para a parte seguinte. Se a peça vai ser apresentada ao vivo ou cabe em vinte slides, use o deck (`templates/deck/`).

## Gramática

Só as classes de `tokens/8020.css`, `assets/regua.css` e `assets/book.css`. Um `<style>` local por página cobre o que a camada não tem, consumindo papéis semânticos (`var(--ink)`, nunca a cor crua).

- **Hub.** `section.hub#hub` com `.container.folha`. No `.miolo`: `p.fonte` (tipo de peça e data), `h1` com a assinatura da marca no último termo (`<em>Cerrado</em>`), `.capa-meta`, e o `.mapa` com uma `.parte` por parte (`.num`, `h3` com link para a parte, `ol` de capítulos com `.quadrado` de estado, link `.peso[data-t]` para `partes/parte-N.html#cap-M` e `.est` com o tempo, `.tempo` da parte). Na `aside.margem.fixa`: `.n` com o total de partes, o bloco `.continuar` (`p#continuar-texto` e `a.tinta#continuar-acao`), a legenda dos quadrados e a frase de privacidade. Depois, `.container.hub-foto` com a imagem em 21 por 9 e a `.legenda`. Uma `section.bloco` "Como ler" fecha o hub com a leitura de partida em `.prosa` e a margem com os atalhos. Sem cartão, sem grade de cartões.
- **Parte.** `body.book[data-book][data-hub="../index.html"]`, `a.pular`, `.progresso-leitura#progresso`, `header.topo` com `.marca`, `.trilha` e `.direita`, `main#conteudo`, o diálogo `.atalhos#atalhos[hidden]`, `footer.rodape`, e os dois scripts `book.js` e `dado.js` no fim. A abertura é `section.abre-parte` com `.numeral`, o `h1` da parte, a `.frase` com o núcleo em `<strong>` e a `aside.margem.fixa` com os tempos dos capítulos e a base.
- **Capítulo.** `article.capitulo#cap-N[data-titulo]`. A `.cabeca` traz `p.cap-meta` (número e tempo), o `h2` e a `aside.margem` com o que o capítulo prova. O corpo é uma `.folha.com-notas` com `.miolo.pilha-l` e `aside.margem`.
- **Prosa e notas.** `.prosa` com parágrafos de 17 px. A chamada é `a.chamada[href="#nN"][id="rN"]`; a nota é `.nota-m#nN[data-ref="rN"]` na margem, com o número em `<b>`. O book.js alinha cada nota ao parágrafo que a chama e as afasta quando se sobrepõem. O `.numero-em-linha` mora dentro da prosa quando o número faz parte da frase.
- **Figura e legenda na margem.** `.figura` com `img` (16 por 9; `.tres-dois` para 3 por 2). Quando a legenda vai para a margem, a figura recebe `id="fig-N"` e a margem recebe `.nota-m.legenda-m[data-ref="fig-N"]`. Figura com dado: `.figura` com `.cabeca` (`h3` e `.sub`), `.grafico` com o SVG (`role="img"`, `aria-label`, `<title>`), `.leitura` com a leitura em palavras, `details.razao` com a `.tabela` e `.fonte`. Marca com `data-leitura` reescreve a `.leitura` sob o ponteiro ou o foco (dado.js). Tabela de dado dentro de `.figura` leva `.leitura` e `.fonte`; ela mesma é o livro-razão.
- **Scrollytelling.** `.folha.scrolly` com `.miolo > .fixo` (a figura que fica presa) e `.margem.passos-m` com os passos `.passo-m[data-estado="N"][data-leitura]`. O book.js copia o `data-estado` do passo do meio da tela para o `.fixo` e o `data-leitura` para a `.leitura`. Os estados são regras de CSS no `<style>` da página, só com papéis semânticos: `.fixo[data-estado="1"] #p-b1 rect { fill: var(--accent); }`. Nenhum JavaScript próprio. `data-estado-estreito` no `.scrolly` diz que estado mostrar abaixo de 900 px, onde a figura deixa de ser fixa e os passos aparecem todos.
- **Fichas.** `.miolo.fichas` com uma `.ficha` por público: retrato 4 por 5, `h3` com o nome do público, `.papel`, `.frase` com o núcleo em `<strong>` e `dl` com onde está, o que já sabe e o que o plano faz.
- **Foto ao lado.** `.lado` com `.figura` (foto e `.legenda`) e `.prosa`, metade a metade.
- **Momento.** `section.momento.tema-laranja` com `.container.folha`, `p.statement` com o núcleo em `<strong>` e a margem fixa. Um por parte, no máximo.
- **Recap.** `section.capitulo#recap[data-titulo]` com `h2` "O que a parte N mostrou", `ol.recap` com três achados escritos por inteiro (o título de cada um em `<strong>`), `p.fonte` com o método e a margem fixa.
- **Navega.** `nav.navega` dentro do recap: `a` anterior e `a.prox`, cada um com `.rot` e `.tit`. A parte 1 volta ao hub; a última aponta "Voltar ao início" para `../index.html`.

## Esqueleto do exemplo

| Parte | Capítulo | Tempo | O que prova |
|---|---|---|---|
| 1. Leitura do desafio | A empresa que chega ao Cerrado | 4 min | A rede é lembrada onde está há mais tempo; a comunicação foi feita loja a loja, sem sistema |
| 1. Leitura do desafio | O que muda na comunicação da rede | 5 min | O plano troca seis comunicações locais por uma presença de rede sem tirar o gerente da decisão |
| 2. Diagnóstico | Onde a marca já é lembrada | 4 min | A marca é primeira em quatro das seis cidades; as duas exceções têm a mesma causa |
| 2. Diagnóstico | De onde vêm os clientes novos | 7 min | Quatro canais trazem 85% dos clientes novos; nenhum é o que leva a maior verba |
| 2. Diagnóstico | Três públicos, uma frase para cada | 8 min | Os três públicos já existem na cidade; o plano dá a cada um uma frase e um lugar |
| 3. Mensagem, canais e cronograma | A mensagem que cabe na porta do armazém | 6 min | Uma frase vale para seis cidades quando cada loja adapta o exemplo; o fluxo da pauta cabe na redação pequena |
| 3. Mensagem, canais e cronograma | Cronograma de entrada | 7 min | Quatro fases, R$ 546 mil e três metas cabem entre setembro e abril |

O hub soma 41 minutos: 9, 19 e 13.

## Navegação e teclado

- **Trilha.** No topo, `.trilha` mostra a peça, a parte e o capítulo visível (`span.atual#trilha-atual`, atualizado pelo book.js conforme o leitor rola).
- **Progresso.** `.progresso-leitura#progresso` é a linha de 2 px no alto da página; a largura acompanha a rolagem.
- **Continuar de onde parou.** O `data-book` do `body` é a chave que guarda no navegador o último capítulo visto (página e id). No hub, o bloco `.continuar` passa a dizer "Você parou em ..." e o link leva ao capítulo; o mapa marca o capítulo com o quadrado de tinta e os anteriores como lidos. O book.js guarda a página relativa ao hub (`partes/parte-2.html`) e casa página e id, porque os ids de capítulo se repetem entre as partes.
- **Teclado.** `j` vai ao próximo capítulo, `k` ao anterior, `h` volta ao hub, `?` abre e fecha a lista de atalhos, `Esc` fecha. Nas partes, `h` usa o `data-hub` do `body` (`../index.html`); no hub, rola até `#hub`.
- **Pular.** `a.pular` leva ao `main#conteudo` para quem navega por teclado.

## Momentos e tetos

- Um `section.momento.tema-laranja` por parte, no máximo, nunca ao lado de outro momento. No exemplo, a parte 1 não tem, a parte 2 tem a mensagem-mãe e a parte 3 fecha com a frase do orçamento.
- No máximo três momentos de acento (laranja) por página. O laranja funcional (quadrado de estado, `.linha-tempo li.agora`) e o 20 do dado não contam.
- O 20 em laranja, um por gráfico: uma barra, uma linha ou o grupo que a leitura nomeia. Rampa `d1` a `d4` para o resto.
- Branco sobre laranja só a partir de 24 px; o texto pequeno dentro do momento é preto pelos papéis da camada.
- Headings em ordem: `h1` uma vez por página (o título do hub ou da parte), `h2` para capítulo, recap e "Como ler", `h3` para figura, ficha e parte no mapa.
- Nada abaixo de 11,5 px, inclusive texto de SVG depois da escala do viewBox. Quando a coluna aperta, a régua não aumenta a fonte (isso transbordaria o viewBox): o gráfico para de encolher e rola dentro da própria caixa, com 620 px de largura mínima e 900 px nos diagramas de viewBox 1088.

## Impressão

A camada já cuida do essencial: topo, progresso, diálogo, botão de continuar e navegação somem; cada `.capitulo` começa em página nova; a `.folha` vira duas colunas, quatro de conteúdo para uma de margem (a margem fica com 20 por cento); as notas voltam ao fluxo; o laranja do dado vira hachura. Para gerar o PDF de uma parte:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="parte-1.pdf" \
  "http://localhost:PORTA/templates/book/padrao/partes/parte-1.html"
```

Gere um PDF por página (hub e partes) e leia página a página: o scrollytelling imprime no estado inicial, com todos os passos visíveis.

## Checklist de saída

- [ ] Copiou a pasta inteira e trocou todo o conteúdo fictício, inclusive `alt`, `aria-label`, `<title>` e `data-leitura`?
- [ ] Caminhos certos: hub em `../../../`, partes em `../../../../`, `data-hub="../index.html"` em toda parte?
- [ ] `data-book` com a chave da peça nova em todas as páginas, e os links do mapa apontando para `partes/parte-N.html#cap-M`?
- [ ] Todo capítulo com tempo de leitura, o que prova na margem, notas alinhadas, pelo menos uma figura ou dado com `.leitura` e livro-razão, e `.fonte`?
- [ ] Recap com três achados escritos por inteiro e o método; `nav.navega` em toda parte?
- [ ] Um momento por parte no máximo; até três acentos por página; um 20 por gráfico?
- [ ] SVG de dado com `role="img"`, `aria-label` e `<title>`; decorativo com `aria-hidden="true"`; toda `img` com `alt` descritivo?
- [ ] Sem travessão, sem anglicismo evitável, acentuação conferida em caixa alta e em atributos?
- [ ] Verificado em 1440, 900 e 600 sem rolagem horizontal, console limpo, scrollytelling trocando de estado, `?`, `j`, `k` e `h` respondendo?
- [ ] PDF gerado do hub e de cada parte, lido página a página?
