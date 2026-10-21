# Contrato do book padrão

Template de book do 8020-DS 4.1. O exemplo é o "Plano de presença de marca no Cerrado", book de plataforma de comunicação para a Casa do Campo, julho de 2026: três partes e sete capítulos, numerados de 1 a 7. Conteúdo e imagens são fictícios.

## Quando usar

Peça longa de leitura assíncrona: plataforma de comunicação, relatório de território, diagnóstico extenso, qualquer material que o leitor percorre no próprio ritmo em vez de acompanhar uma apresentação. O book abre num hub (`index.html`) e se desdobra em partes (`partes/parte-N.html`), cada uma com dois ou três capítulos e a navegação para a parte seguinte. O hub com partes é o padrão; book curto pode correr numa página só, com a mesma gramática. Se a peça vai ser apresentada ao vivo ou cabe em vinte slides, use o deck (`templates/deck/`).

Papel claro por padrão. Quando a peça vai ser lida na tela e pede o escuro, a classe `noite` no `body` troca o substrato (regra 1); a impressão volta ao papel claro sozinha.

## Gramática

Só as classes de `tokens/8020.css`, `assets/regua.css` e `assets/book.css`. Um `<style>` local por página cobre o que a camada não tem, consumindo papéis semânticos (`var(--ink)`, nunca a cor crua).

- **Hub.** `section.hub#hub` com `.container.folha`. No `.miolo`: `p.fonte` (tipo de peça e data), `h1` descritivo e sem itálico, `.capa-meta` (para quem e o tamanho da peça), e o `.mapa` com uma `.parte` por parte (`.num`, `h3` com link para a parte, `ol` de capítulos com `span.n` e o número contínuo do capítulo, e o link `.peso[data-t]` para `partes/parte-N.html#cap-M`). Na `aside.margem.fixa`: `.n` com o total de partes, uma frase com o que as partes cobrem e `a.tinta.comecar` para a parte 1. Depois, `.container.hub-foto` com a imagem em 21 por 9 e a `.legenda`. Sem tempo de leitura, sem "continuar de onde parou" e sem seção que explica como ler (regras 22 e 22a). Sem cartão, sem grade de cartões.
- **Parte.** `body.book[data-hub="../index.html"]`, `a.pular`, `.progresso-leitura#progresso`, `header.topo` com `.marca`, `.trilha` e `.direita`, `main#conteudo`, o diálogo `.atalhos#atalhos[hidden]`, `footer.rodape`, e os dois scripts `book.js` e `dado.js` no fim. A abertura é `section.abre-parte` com `.numeral`, o `h1` da parte, a `.frase` com o núcleo em `<strong>` e a `aside.margem.fixa` com os capítulos da parte ("Capítulos 3 a 5" e os nomes).
- **Capítulo.** `article.capitulo#cap-N[data-titulo]`, com N contínuo pela peça inteira: a parte 2 começa no capítulo 3. A `.cabeca` traz `p.cap-meta` com `<b>Capítulo N</b>` e o `h2`. O achado do capítulo abre a prosa, com o núcleo em `<strong>`; nada de rótulo que anuncia o que o capítulo prova. O corpo é uma `.folha.com-notas` com `.miolo.pilha-l` e `aside.margem`. Todo capítulo tem pelo menos uma figura, gráfico, tabela ou número em destaque (regra 15a).
- **Prosa e notas.** `.prosa` com parágrafos de 17 px. A chamada é `a.chamada[href="#nN"][id="rN"]`; a nota é `.nota-m#nN[data-ref="rN"]` na margem, com o número em `<b>`. O book.js alinha cada nota ao parágrafo que a chama e as afasta quando se sobrepõem. O `.numero-em-linha` mora dentro da prosa quando o número faz parte da frase.
- **Figura e legenda na margem.** `.figura` com `img` (16 por 9; `.tres-dois` para 3 por 2). Quando a legenda vai para a margem, a figura recebe `id="fig-N"` e a margem recebe `.nota-m.legenda-m[data-ref="fig-N"]`. Figura com dado: `.figura` com `.cabeca` (`h3` e `.sub`), `.grafico` com o SVG (`role="img"`, `aria-label`, `<title>`), `.leitura` com a leitura em palavras, `details.razao` com a `.tabela` e `.fonte`. Marca com `data-leitura` reescreve a `.leitura` sob o ponteiro ou o foco (dado.js). Tabela de dado dentro de `.figura` leva `.leitura` e `.fonte`; ela mesma é o livro-razão.
- **Scrollytelling.** `.folha.scrolly` com `.miolo > .fixo` (a figura que fica presa) e `.margem.passos-m` com os passos `.passo-m[data-estado="N"][data-leitura]`. O book.js copia o `data-estado` do passo do meio da tela para o `.fixo` e o `data-leitura` para a `.leitura`. Os estados são regras de CSS no `<style>` da página, só com papéis semânticos: `.fixo[data-estado="1"] #p-b1 rect { fill: var(--accent); }`. Nenhum JavaScript próprio. `data-estado-estreito` no `.scrolly` diz que estado mostrar abaixo de 900 px, onde a figura deixa de ser fixa e os passos aparecem todos.
- **Fichas.** `.miolo.fichas` com uma `.ficha` por público: retrato 4 por 5, `h3` com o nome do público, `.papel`, `.frase` com o núcleo em `<strong>` e `dl` com onde está, o que já sabe e o que o plano faz.
- **Foto ao lado.** `.lado` com `.figura` (foto e `.legenda`) e `.prosa`, metade a metade.
- **Momento.** `section.momento.tema-laranja` com `.container.folha`, `p.statement` com o núcleo em `<strong>` e a margem fixa com um dado, sem rótulo de método. Um por parte, no máximo.
- **Recap, opcional.** Só depois de um capítulo longo: `ol.recap` com até três achados escritos por inteiro, o título de cada um em `<strong>`. O exemplo não tem, porque os capítulos são curtos (regra 28).
- **Navega.** `section.bloco.fim-parte` com `nav.navega`: `a` anterior e `a.prox`, cada um com `.rot` e `.tit`. A parte 1 volta ao hub; a última aponta "Voltar ao início" para `../index.html`.

## Esqueleto do exemplo

| Parte | Capítulo | O achado que abre a prosa |
|---|---|---|
| 1. Leitura do desafio | 1. A empresa que chega ao Cerrado | A rede é lembrada onde está há mais tempo; a comunicação foi feita loja a loja, sem sistema |
| 1. Leitura do desafio | 2. O que muda na comunicação da rede | O plano troca seis comunicações locais por uma presença de rede sem tirar o gerente da decisão |
| 2. Diagnóstico | 3. Onde a marca já é lembrada | A marca é primeira em quatro das seis cidades; as duas exceções têm a mesma causa |
| 2. Diagnóstico | 4. De onde vêm os clientes novos | Quatro canais trazem 85% dos clientes novos; nenhum é o que leva a maior verba |
| 2. Diagnóstico | 5. A quem o plano fala, e o que diz a cada um | Os três públicos já existem na cidade; o plano dá a cada um uma frase e um lugar |
| 3. Mensagem, canais e cronograma | 6. A mensagem que cabe na porta do armazém | Uma frase vale para seis cidades quando cada loja adapta o exemplo; o fluxo da pauta cabe na redação pequena |
| 3. Mensagem, canais e cronograma | 7. Cronograma de entrada | Quatro fases, R$ 546 mil e três metas cabem entre setembro e abril |

## Navegação e teclado

- **Trilha.** No topo, `.trilha` mostra a peça, a parte e o capítulo visível (`span.atual#trilha-atual`, atualizado pelo book.js conforme o leitor rola).
- **Progresso.** `.progresso-leitura#progresso` é a linha de 2 px no alto da página; a largura acompanha a rolagem.
- **Nada guardado.** O book não guarda no navegador onde o leitor parou e não mostra tempo de leitura (regra 22a). O mapa do hub é sumário, não painel de progresso.
- **Teclado.** `j` vai ao próximo capítulo, `k` ao anterior, `h` volta ao hub, `?` abre e fecha a lista de atalhos, `Esc` fecha. Nas partes, `h` usa o `data-hub` do `body` (`../index.html`); no hub, rola até `#hub`.
- **Pular.** `a.pular` leva ao `main#conteudo` para quem navega por teclado.

## Momentos e tetos

- Um `section.momento.tema-laranja` por parte, no máximo, nunca ao lado de outro momento. No exemplo, a parte 1 não tem, a parte 2 tem a mensagem do plano e a parte 3 fecha com a frase do orçamento.
- No máximo três momentos de acento (laranja) por página. O laranja funcional (quadrado de estado, `.linha-tempo li.agora`) e o 20 do dado não contam.
- O 20 em laranja, um por gráfico: uma barra, uma linha ou o grupo que a leitura nomeia. Rampa `d1` a `d4` para o resto.
- Branco sobre laranja só a partir de 24 px; o texto pequeno dentro do momento é preto pelos papéis da camada.
- Headings em ordem: `h1` uma vez por página (o título do hub ou da parte), `h2` para capítulo, `h3` para figura, ficha e parte no mapa.
- Nada abaixo de 11,5 px, inclusive texto de SVG depois da escala do viewBox. Quando a coluna aperta, a régua não aumenta a fonte (isso transbordaria o viewBox): o gráfico para de encolher e rola dentro da própria caixa, com 620 px de largura mínima e 900 px nos diagramas de viewBox 1088. Na largura de leitura da peça, nenhum gráfico rola (regra 47a).

## Impressão

A camada já cuida do essencial: topo, progresso, diálogo, o link de começar e a navegação somem; a peça noite volta ao papel claro; cada `.capitulo` começa em página nova; a `.folha` vira duas colunas, quatro de conteúdo para uma de margem (a margem fica com 20 por cento); as notas voltam ao fluxo; o laranja do dado vira hachura.

O PDF sai quando a peça vai circular em PDF, pelo motor do sistema, que imprime o hub e cada parte na ordem do mapa, junta tudo num arquivo e confere páginas, tamanho e fonte:

```bash
python3 imprimir.py caminho/do/book/index.html --previa
```

Leia a prévia página a página: o scrollytelling imprime no estado inicial, com todos os passos visíveis.

## Checklist de saída

- [ ] Copiou a pasta inteira e trocou todo o conteúdo fictício, inclusive `alt`, `aria-label`, `<title>` e `data-leitura`?
- [ ] Caminhos certos: hub em `../../../`, partes em `../../../../`, `data-hub="../index.html"` em toda parte?
- [ ] Os links do mapa apontando para `partes/parte-N.html#cap-M`, com M contínuo de 1 a N pela peça inteira?
- [ ] Todo capítulo com o achado na primeira frase, notas alinhadas, pelo menos uma figura ou dado com `.leitura` e livro-razão, e `.fonte`?
- [ ] Nenhum tempo de leitura, nenhum "continuar", nenhuma versão, nenhum "Base:" de colofão, nenhum título com itálico?
- [ ] Recap só depois de capítulo longo; `nav.navega` em toda parte?
- [ ] Um momento por parte no máximo; até três acentos por página; um 20 por gráfico?
- [ ] SVG de dado com `role="img"`, `aria-label` e `<title>`; decorativo com `aria-hidden="true"`; toda `img` com `alt` descritivo?
- [ ] Sem travessão, sem anglicismo evitável, acentuação conferida em caixa alta e em atributos?
- [ ] Verificado nas larguras em que a peça vai ser lida (900 e 600 quando ela circular no celular), sem rolagem horizontal na página nem em gráfico, console limpo, scrollytelling trocando de estado, `?`, `j`, `k` e `h` respondendo?
- [ ] Se a peça vai circular em PDF: gerado pelo `imprimir.py`, sem erro, e lido página a página na prévia?
