# Regras do 8020-DS 4.0

As regras inegociáveis do sistema de design da 80 20 Marketing. Quem gera uma peça com este sistema segue tudo o que está aqui. Quando houver conflito entre uma vontade pontual e uma regra, a regra vence.

A numeração de 1 a 29 é a da versão 3 e continua valendo: as regras que sobreviveram estão nos mesmos números, com o texto ajustado onde a 4.0 mudou. O que a 4.0 acrescenta começa na regra 30. Quem vem de uma peça da versão 3 lê o [guia de migração](MIGRACAO.md) antes de converter qualquer coisa.

Duas passadas fecham toda peça: `verificar.py` na estrutura e no texto, `verificar-geometria.js` na geometria. A tabela do fim relaciona cada checagem à regra que ela cobra.

## Marca

1. O papel claro é o substrato de toda peça: fundo off-white, tinta em chumbo quente. O laranja `#fa4616` é o momento e o acento; como fundo, só dentro de um momento (`tema-laranja`), nunca o substrato da peça. Nunca outro laranja.
2. A tinta da base é o chumbo quente; o branco é a tinta dos momentos (`tema-laranja`, `tema-escuro`). Todo par de texto e fundo sai da matriz de contraste (`tokens/brand.json`), que é medida e não estimada. Branco sobre o laranja vale a partir de 24 px, ou de 19 px em peso 700; abaixo disso o texto dentro do momento laranja é preto, e a camada já resolve.
3. A imagem é sempre reta: retângulo sem raio, sem borda e sem máscara. Foto de página inteira leva véu na base para o texto ficar legível; foto ao lado de texto ocupa metade da folha. Toda imagem gerada é marcada como ilustrativa na legenda ou na fonte, e nenhuma imagem traz pessoa real, marca d'água ou texto legível. Ver `patterns/imagens.html`.
4. Sem gradiente. A superfície é chapada: papel, areia, chumbo, laranja. O que parecia profundidade vem do filete de 1 px e da diferença de tinta. As únicas rampas contínuas que o sistema aceita são funcionais: o véu sobre a foto, a hachura que substitui o laranja na impressão e o preenchimento vazio de imagem.
5. Montserrat é a única família, do corpo ao display. O salto do último termo para o itálico é assinatura, marcado no HTML com `<em>`, não acaso. Aparece em título de capa, de hero e de abertura de parte, uma vez por peça.
6. A paleta é fechada: laranja, laranja aprofundado, branco, preto e chumbos profundos. Sem azul, verde, ouro, areia ou vermelho. O acento é escasso: no máximo três momentos de acento por página ou slide em peça cliente. A escassez é o que dá impacto. Os chumbos profundos cobrem as variações já registradas em `tokens/brand.json`: `#120e0b` é o chão do momento escuro, e `#faf7f2`, `#1a140f` e `#2a201a` são os tons do papel claro. É a mesma família de chumbo quente e papel, não cores novas: a paleta segue fechada.
6a. O laranja e o escuro entram na peça como momentos: as classes `tema-laranja` e `tema-escuro` aplicadas a um slide, seção ou card (aparte, respiro fotográfico, statement, capa quando a peça pedir). Momento de página inteira entra no máximo uma vez por capítulo e nunca em dois slides seguidos. A faixa laranja de separatriz é uma por capítulo, e a capa pode ter a sua. Em bloco menor, o momento conta no teto de acento da regra 6. A contracapa não conta: usa `--floor` por contrato próprio.
6b. O laranja tem quatro papéis e só eles: momento, ação primária dentro do momento, estado atual e o 20 do dado. O laranja funcional (o quadrado de estado, o passo atual, o filete de erro, o 20 de um gráfico) fica fora do teto da regra 6, porque informa em vez de decorar. Laranja em qualquer outro lugar é erro.
7. A logo 80 20 está sempre presente e nunca recolorida: assume a tinta do contexto, escura na base clara, branca dentro dos momentos. Topo à esquerda na peça; co-marca do cliente topo à direita; contracapa com a logo e os três endereços (São Paulo, Campo Grande, Cuiabá).

## Construção e acessibilidade

8. Gráfico e diagrama em SVG real (`<rect>`, `<path>`, `<polyline>`, `<circle>`, `<polygon>`), nunca uma `div` com largura em porcentagem.
8a. Diagramas usam ângulos retos: conectores em segmentos retos, com dobra em ângulo reto quando mudam de direção, nunca curva. Espaço generoso entre as linhas e os rótulos.
8b. Sem sombras em parte alguma. A profundidade vem da cor (superfície, chumbo) e do filete de 1 px, nunca de `box-shadow`.
8c. Em SVG, cor de texto via `style` inline ou por classe, nunca via atributo `fill`: atributo de apresentação perde para regra de classe CSS, e o texto some sobre a caixa de acento.
8d. Bloco de slide com `height: 100%` e padding leva `box-sizing: border-box`, senão o padding soma à altura, o conteúdo estoura a zona segura e o rodapé engole texto.
8e. Animação em dois registros, ambos sob `@media screen and (prefers-reduced-motion: no-preference)` para a impressão sair estática: entrada quando o slide abre (fade e subida em cascata, linha que se desenha, ponto que surge) e movimento constante só onde ele ajuda a leitura. Só `transform` e `opacidade` se movem.
8f. O visualizador de deck é a casa: moldura em chumbo com o slide inteiro no centro, controles fora do slide (marca, peça e capítulo no topo; contador, teclas e trilho na base), miniaturas na tecla `o`, tela cheia em `f`, visão do apresentador em `p`, atalhos em `?`. Navegação pelas setas do teclado, sem pontos de progresso e sem avanço por clique no slide.
9. Toda seta vem de um `<marker>` em `<defs>`, com `orient="auto-start-reverse"`. O triângulo desenhado à mão não acompanha a curva.
10. SVG de dado leva `role="img"`, `aria-label` descritivo e `<title>` interno. SVG decorativo leva `aria-hidden="true"`. Toda `img` leva `alt` descritivo, ou `alt=""` quando o nome já está ao lado.
11. Toda animação respeita `prefers-reduced-motion`. O conteúdo essencial (número, texto, geometria do gráfico) vive no HTML e renderiza sem JavaScript: o valor final fica escrito no elemento, o `data-count` é só realce.
12. Os títulos seguem a hierarquia (`h1` antes de `h2` antes de `h3`), sem pular nível, com um `h1` por página.
13. As camadas de layout (`assets/regua.css`, `assets/deck.css`, `assets/book.css`) consomem só papéis semânticos (`--paper`, `--ink`, `--accent` e companhia), nunca a cor crua `--8020-*`. O `<style>` local de uma peça segue a mesma regra. Por isso qualquer variante de cor roda em qualquer layout.

## Facilitação visual (metodologia)

14. O número grande e a frase que o nomeia são um par indissociável. O número nunca aparece sozinho: ao lado dele, o rótulo diz o que se mede e o texto diz por que importa. Dentro da prosa, o número entra na frase pelo `.numero-em-linha`.
15. Toda declaração massiva vem acompanhada de texto que explica e de um gráfico ou dispositivo que mastiga. Densidade de livro digital, não de slides.
16. Toda peça tem arco: início, meio e fim. O ritmo alterna o denso e o leve.
17. A clareza inline é premissa, não acabamento: o leitor lê qualquer trecho solto e se localiza, porque a referência nomeia os itens na própria frase.

## Editorial

18. Português do Brasil com acentuação correta, sempre, inclusive em caixa-alta, em título de display e dentro de `alt`, `aria-label` e `title`.
19. Sem travessão (em-dash). No lugar dele: dois-pontos, vírgula, parênteses ou ponto.
20. Sem anglicismo evitável. Nomes próprios por extenso (Banco do Brasil, não a sigla). Sem abreviação em peça cliente.
21. O título é descritivo: diz do que o slide ou a seção trata, sem inventariar ("Os seis segmentos") e sem virar enigma. O achado não mora no título: mora na frase central do slide ou na abertura da seção. Título que precisa ser decifrado é título errado.
22. Sem autorreferência ao próprio documento. O texto lidera pelo assunto, não pelo veículo.
23. Prosa fluida, não staccato. Toda afirmação forte tem lastro na fonte. Quando não há dado que sustente, suaviza-se ou remove-se.
24. A voz fala para o cliente final, em registro consultivo. Observa e sugere; não acusa nem crava conclusão sem evidência. O nome da 80 20 não aparece no texto corrido de peça cliente: aparece na logo, na capa e na contracapa.
25. **Clareza radical, sem figura de linguagem.** Nada de paradoxo ("quem tenta mudar tudo não muda nada"), nada de metáfora ou figura difusa (terreno, palco, espinha, guardião, anatomia, zona cinzenta, matéria-prima, contrato como imagem), nada de personificação de conceito ("a estatística conta", "a leitura sabe"). Dizer o que é, literalmente. Explicar e educar vence impressionar.
26. **Peça funcional tem nome funcional.** Sumário chama-se Sumário, índice chama-se Índice, conclusão chama-se conclusão. Sem título criativo para seção de navegação.
27. **Palavra difícil ou pouco usada no contexto sai.** "Eleitos" vira "escolhidos", "declarada" vira "definida". O leitor de chão de fábrica e o conselheiro leem a mesma frase sem tropeço. O termo "declarada" e derivações não entram em peça.

## Didática (deck longo)

28. Todo capítulo fecha com um slide de conclusão rotulado "O que aprendemos no capítulo NN", com cada aprendizado escrito por inteiro, compreensível se lido isoladamente, e a fonte do método junto.
29. O deck é sequencial e numerado: número do slide e capítulo no rodapé de todos os slides, separatriz numerada por capítulo, sumário no início e página única de fechamento com a estratégia inteira em um esquema com hierarquia (tese no topo, desdobramentos abaixo, acordo entre as partes na base, conectores anotados). Capa e contracapa são descritivas: dizem nome, cliente, data e o que a peça contém.

## A Régua 80/20 (novo na 4.0)

30. **A grade é quatro para um.** Folha e slide se dividem em quatro partes de conteúdo e uma de margem viva. A margem carrega dado, nota, estado, progresso, legenda e o cromo do deck; nunca decoração e nunca sobra. Abaixo de 900 px a margem vira uma linha acima do conteúdo, e as notas viram dobras.
31. **O filete de 1 px é o separador padrão.** Cartão só para coleção de itens iguais, sem borda, com raio zero e nunca aninhado. Fora do sistema: barra lateral colorida, caixa de ícone, pílula, cápsula, deslocamento do bloco ao passar o ponteiro e qualquer moldura que exista só para separar.
32. **O filete conta o estado.** Todo controle textual assenta sobre uma linha que muda com o estado: fina em repouso, cheia sob o ponteiro, grossa no foco, pontilhada quando desabilitado, laranja no erro, varrendo quando carrega. O anel de foco de 2 px com 2 px de afastamento nunca é removido.
33. **Estado é peso, não cor.** Navegação, abas, sumário e lista de capítulos mudam de peso tipográfico para dizer onde o leitor está. A largura fica reservada no peso máximo, para o texto não empurrar os vizinhos quando muda.
34. **O botão primário tem registro.** Retângulo reto, com a chapa deslocada 4 px sob o ponteiro e assentada no clique, como impressão fora de registro. Três níveis de ação e nada além: primária com registro, secundária sobre filete, terciária como texto sublinhado.
35. **Estado se escreve em palavras.** "Enviar", "enviando", "enviado às 14:32". Erro traz a frase que resolve, não o código. Cor sozinha nunca informa estado: vem sempre com forma (filete, peso, quadrado) ou com a palavra.
36. **Um ícone só.** O quadrado de 8 px, em quatro preenchimentos: tinta é informação, laranja é atenção, contorno é feito, meta é parado. Nenhuma biblioteca de ícones, nenhum pictograma decorativo.

## Deck (novo na 4.0)

37. **Cinco registros, escolhidos pelo papel do slide na narrativa, não por gosto.** Faixa à esquerda para evidência; faixa no topo para conteúdo largo (tabela, fases, fluxo, esquema); quieto para navegação e recap; cheio com momento para o aparte, o respiro e a mensagem-mãe; faixa laranja para capa e separatriz.
38. **Toda faixa carrega três coisas: capítulo, título descritivo e frase central.** A frase central é obrigatória, tem o núcleo em `<strong>` e é onde o achado do slide aparece. Faixa sem frase é slide sem tese.
39. **O sistema escreve o cromo.** Contador, trilho, moldura, miniaturas, atalhos e visão do apresentador saem do `deck.js`. O autor escreve só os slides, e a numeração sobrevive a inserção e remoção. Sem JavaScript os slides empilham na vertical e continuam legíveis.
40. **O deck imprime do mesmo arquivo**, um slide por página em 1280 por 720, com a faixa colorida, o contador no rodapé e o laranja do dado virando hachura. Não existe arquivo de impressão separado.

## Dado (novo na 4.0)

41. **O laranja é o 20.** Um elemento por gráfico, o mesmo que a leitura em palavras nomeia. O resto sai da rampa de uma tonalidade em quatro degraus (100, 64, 40 e 20 por cento). Cor nunca é a variável de categoria: para dizer duas categorias, use posição, tamanho ou painéis separados. Dado negativo é chumbo, nunca vermelho.
42. **Toda figura de dado traz a leitura em palavras e o livro-razão.** A leitura fica visível em repouso, porque a página tem de informar parada; o ponteiro só a reescreve. O livro-razão é a tabela sob a figura, dentro de um `details`, com a fonte. No slide a conta é outra: o valor vem escrito na própria marca e a fonte fica ao pé, porque a sala não abre tabela.
43. **Sem pizza, sem eixo duplo, sem 3D, sem série em gradiente.** Barra sempre parte da linha do zero. Escala truncada só com o corte marcado. Unidades em 80 e 20 quando o dado permitir.
44. **Anotação em duas formas e no máximo duas por gráfico:** a nota com guia até o ponto, e a linha de evento (filete vertical no instante, nota no alto). A guia nunca cruza uma série.
45. **Transição entre estados move a mesma marca em 480 ms**, e a cor fica com a entidade, não com o passo. Com `prefers-reduced-motion` a troca é imediata.
46. **No momento laranja a rampa de dado é de preto** (100, 64, 40 e 20 por cento) e o 20 é branco, porque a rampa branca não separa quatro degraus sobre o laranja. Com dado no momento laranja, no máximo duas séries mais o 20.

## Limites e verificação (novo na 4.0)

47. **Piso de fonte:** nada abaixo de 11,5 px na página e de 14 px efetivos no slide, medido no tamanho real (texto de SVG multiplicado pela escala do viewBox). A miniatura de um slide não conta: é a imagem do slide, não texto para ler.

47a. **O gráfico não encolhe abaixo da largura em que o menor rótulo passa do piso.** Aumentar a fonte dentro do mesmo viewBox transborda a caixa, então o caminho é o contrário: a caixa para de encolher e o gráfico rola na horizontal dentro dela. Com 13 px de menor texto, 620 px sustentam um viewBox de 640; o diagrama de 1088 precisa de 900, e o gráfico de viewBox pequeno leva `.compacto`, que baixa o piso para 300. A conta é da caixa, não da janela: a mesma coluna estreita aparece no telefone, na grade do catálogo e ao lado da margem do book. No slide, que tem largura fixa e piso próprio, o gráfico não rola.

47b. **Rótulo de topo nunca senta acima de 15 no viewBox:** a parte alta das letras fica fora da caixa do gráfico e o corte aparece na impressão.
48. **Limites de texto por área do slide**, em caracteres com espaço. Passou do limite, o slide corta ou o texto sobrepõe. No book e na página o texto reflui e não há teto: quem manda é a medida de leitura da regra 30.

| Onde | Teto |
|---|---|
| Capítulo mais rótulo (`.cap`) | 30 |
| Título da faixa (`h2`) | 48 |
| Título de slide quieto | 60 |
| Frase central (`.frase`) | 110 |
| Statement | 70 |
| Citação | 120 |
| Item de lista: título e descrição | 50 e 110 |
| Célula de tabela | 40, e seis colunas no registro topo |
| Legenda de foto | 120 |
| Nota do apresentador | 300 |

49. **Nenhum elemento sai dos 1280 por 720**, nenhum texto se sobrepõe a outro e nenhum rótulo de SVG cruza traço ou sai da caixa do próprio SVG. No registro topo a faixa tem 240 px fixos, o conteúdo tem 392 px úteis, o título vai até duas linhas a 36 px e a tabela até seis linhas a 15 px.
50. **Nenhuma peça sai sem as duas passadas do verificador**, com zero erro nas duas: `python3 verificar.py` na estrutura e no texto, `verificar-geometria.js` no Playwright para a geometria do slide. Aviso não bloqueia, mas cada um se lê e se decide.

50a. **Contraexemplo se declara.** Uma página que mostra de propósito o que o sistema recusa marca o bloco com `data-antipadrao`, e o marca também no CSS, entre `/* antipadrão: */` e `/* fim do antipadrão */`. As duas passadas ignoram o que está declarado. Fora dessa marcação não existe exceção: o que o verificador aponta, se corrige. A página `patterns/proibido.html` é o único uso previsto.

## O que o verificador cobra

`verificar.py` lê o HTML da peça e devolve os achados por slide ou por seção. Cada checagem aponta a regra:

| Código | Nível | Regra |
|---|---|---|
| `cor-crua` | erro | 13 |
| `cor-fora-da-paleta` | erro | 6 |
| `gradiente` | erro | 4 |
| `sombra` | erro | 8b |
| `raio` | aviso | 31 |
| `momentos-seguidos` | erro | 6a |
| `momento-repetido-no-capitulo` | erro | 6a |
| `faixa-laranja-repetida` | erro | 6a |
| `acentos-acima-do-teto` | aviso | 6 |
| `barra-em-div` | erro | 8 |
| `svg-fill-em-texto` | erro | 8c |
| `dado-sem-papel`, `dado-sem-titulo` | erro | 10 |
| `svg-decorativo-exposto` | aviso | 10 |
| `seta-sem-marcador` | aviso | 9 |
| `dado-sem-razao`, `dado-sem-leitura` | erro, aviso | 42, na página e no book |
| `dado-sem-fonte` | aviso | 42, no slide |
| `imagem-sem-alt` | erro | 10 |
| `imagem-gerada-sem-marca` | aviso | 3 |
| `heading-fora-de-ordem`, `h1-repetido` | erro | 12 |
| `numero-sem-frase` | erro | 14 |
| `movimento-sem-guarda` | aviso | 11 |
| `travessao` | erro | 19 |
| `sem-acento` | erro | 18 |
| `anglicismo` | aviso | 20 |
| `titulo-com-achado` | aviso | 21 |
| `titulo-com-contagem` | aviso | 21 |
| `autorreferencia` | aviso | 22 |
| `figura-de-linguagem` | aviso | 25 |
| `palavra-dificil` | aviso | 27 |
| `marca-no-texto` | aviso | 24 |
| `faixa-sem-frase` | erro | 38 |
| `limite-de-texto` | erro | 48 |
| `deck-sem-sumario`, `capitulo-sem-separatriz`, `capitulo-sem-recap`, `deck-sem-esquema`, `deck-sem-contracapa` | erro | 28, 29 |
| `slide-sem-notas` | aviso | 8f |
| `deck-sem-script` | erro | 39 |
| `momento-por-parte` | erro | 6a |
| `passo-sem-estado`, `nota-sem-ancora` | erro | 30 |
| `book-sem-chave` | erro | 30 |

As checagens de cor, de teto de acento e de título valem na peça, não no catálogo: a página de catálogo mostra o valor e o teto por definição.

`verificar-geometria.js` roda no Playwright e cobra as regras 47 e 49: caixa fora do slide, texto sobre texto, texto contra traço em SVG, a fonte mínima efetiva e, na página, a rolagem horizontal.
