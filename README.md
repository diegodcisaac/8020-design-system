# 8020-DS 4.1

Sistema de design da **80 20 Marketing** para peças de comunicação: books, decks e páginas. HTML, CSS, JavaScript e SVG puros. Sem build, sem dependência, sem chamada externa: todo arquivo abre direto no navegador e imprime do mesmo arquivo.

O papel claro é o substrato padrão, o chumbo quente é a tinta, o laranja entra como momento e Montserrat vai do corpo ao display. Book e página lidos na tela podem ir para a noite. A paleta é fechada em seis cores, com uma exceção tabelada: o verde e o amarelo do status de execução.

Esta é a versão 4.1. O que muda da 3 para a 4, e da 4.0 para a 4.1, está em [MIGRACAO.md](MIGRACAO.md).

## Comece por aqui

| Se você é | Comece por |
|---|---|
| Um agente ou modelo de linguagem que vai gerar uma peça | [llms.txt](llms.txt), que dá a ordem de leitura |
| Alguém montando uma peça | [GUIA.md](GUIA.md): três perguntas levam ao modo e ao template, e a receita de cada tipo de slide e de seção está lá |
| Alguém que quer entender o sistema | Abra [index.html](index.html) no navegador |
| Alguém convertendo uma peça da versão 3 | [MIGRACAO.md](MIGRACAO.md), antes de tocar em qualquer arquivo |

As regras estão em [RULES.md](RULES.md) e valem em dois modos. No expresso, a peça parte de um template e segue tudo: é o caminho rápido. No sob medida, a composição é desenhada para a peça, e ela segue o núcleo: marca, acessibilidade, facilitação visual, texto e dado.

## O que tem aqui

```
8020-design-system/
  README.md  RULES.md  GUIA.md  MIGRACAO.md  llms.txt  index.html
  verificar.py  verificar-geometria.js  conferir.py  imprimir.py
  tokens/     8020.css  brand.json  gerar-brand.py
  voice/      plataforma.md  tom-de-voz.md  vocabulario.md
  assets/     regua.css  deck.css  deck.js  book.css  book.js  dado.js  pagina.js
              fonts/  logos/  imagens/  mapas/
  patterns/   tipografia  cores  layouts  estados  proibido
              dado  diagramas  imagens  deck  book   (.html) + _catalogo.css
  testes/     README.md  verificador-deve-reprovar.html
  templates/  deck/padrao/     deck.html  CONTRATO.md     19 slides
              deck/editorial/  deck.html  CONTRATO.md     14 slides
              book/padrao/     index.html  partes/  CONTRATO.md
```

Quatro camadas, nesta ordem de dependência. Cada uma consome só o que a de baixo define, e nenhuma usa cor crua.

1. **Tokens.** `tokens/8020.css` define os primitivos, os papéis semânticos, a escala de tipo, a escala de espaço, a forma, o movimento, a rampa de dado e os dois momentos. `tokens/brand.json` repete tudo em três camadas legíveis por máquina, com a matriz de contraste medida par a par; `gerar-brand.py` o produz a partir do CSS.
2. **A Régua 80/20.** `assets/regua.css` é a camada compartilhada: a grade quatro para um, a página, os controles com os estados, a tabela, as listas, o número em linha, o livro-razão e a gramática de dado.
3. **Deck e book.** `assets/deck.css` e `deck.js` dão os cinco registros de slide, o visualizador, as miniaturas, a visão do apresentador e a impressão. `assets/book.css` e `book.js` dão o hub, a margem viva, as notas ao lado do parágrafo e o scrollytelling.
4. **Templates e catálogo.** `templates/` traz três esqueletos completos com contrato. `patterns/` traz as dez páginas do catálogo, com os blocos ao vivo e o código para copiar.

## Como montar uma peça

1. Escolha o modo e o formato pelas perguntas do [GUIA.md](GUIA.md). No modo expresso, copie a pasta inteira do template, não só o arquivo.
2. Leia o `CONTRATO.md` do template e as [regras](RULES.md).
3. Ajuste os caminhos de `tokens/` e `assets/` para a pasta nova, e preencha `data-marca`, `data-peca` e `data-canal` no deck, ou `data-hub` nas partes do book.
4. Escreva dentro das camadas, copiando componente do catálogo em vez de inventar.
5. Rode as duas passadas do verificador nas larguras em que a peça vai ser lida. O PDF sai pelo `imprimir.py` quando a peça vai circular em PDF.

## Verificação

Duas passadas, e zero erro nas duas é a condição de saída da peça.

```bash
python3 verificar.py caminho/da/peca.html
```

`verificar.py` lê o HTML sem abrir navegador e devolve os achados por slide ou por seção, cada um apontando a regra que cobra. São 55 checagens de marca, superfície, dado, acessibilidade, hierarquia, limites de texto e editorial, em cinco escopos (deck, parte de book, hub, página e catálogo). Só biblioteca padrão do Python 3. Aceita `--pasta`, `--so-erros`, `--json`, `--tipo`, `--regras` e `--fragmento` (para peça em construção, que ainda não tem sumário nem esquema), e sai com código 1 quando houver erro.

`verificar-geometria.js` mede o que só a renderização mostra: caixa fora dos 1280 por 720 do slide, texto sobre texto, rótulo de SVG cruzando traço, fonte mínima efetiva e rolagem horizontal, da página e de cada gráfico. Roda no Playwright, com `__URL__` e `__DIR__` trocados; o Playwright não abre `file://`, então a peça precisa de um servidor local (`python3 -m http.server` na pasta basta).

`conferir.py` cuida do repositório em vez da peça: conta o que existe (checagens, páginas, formas, regras, slides) e confere contra o que este README, o guia, o `llms.txt` e o índice afirmam, mais os links internos e o teste de regressão. Número de documento envelhece calado, e já envelheceu duas vezes aqui.

```bash
python3 conferir.py
```

`testes/verificador-deve-reprovar.html` é o teste de regressão: seis slides escritos de propósito para reprovar, que disparam 41 das 55 checagens. Se ele parar de reprovar, o verificador quebrou.

## Impressão

Deck e book imprimem do mesmo arquivo. O deck pagina um slide por página em 1280 por 720; o book quebra página antes de cada capítulo e vira duas colunas, quatro de conteúdo para uma de margem, sempre no papel claro, inclusive a peça noite. O PDF sai quando a peça vai circular em PDF, e o motor fica pronto para isso:

```bash
python3 imprimir.py caminho/da/peca/deck.html
python3 imprimir.py caminho/do/book/index.html --previa
```

`imprimir.py` acha o Chrome, espera fonte e script carregarem, imprime e confere o resultado: número de páginas, tamanho da página e Montserrat embutida. No book, imprime o hub e cada parte na ordem do mapa e junta tudo num arquivo só. `--previa` gera uma imagem de cada página para a leitura página a página. Só biblioteca padrão do Python; o Chrome é o motor.

## Conteúdo dos exemplos

Todo conteúdo dos três templates é fictício: a "Casa do Campo" é uma rede de lojas inventada para o exemplo, e os números, nomes, citações e endereços não correspondem a nada real. As fotografias em `assets/imagens/` foram geradas e estão marcadas como ilustrativas; nenhuma retrata pessoa real. Os endereços da contracapa vêm como preenchimento entre colchetes, para ninguém publicar por engano os do exemplo.

## Base geográfica

`assets/mapas/` traz a malha municipal de Goiás e de Mato Grosso do Sul em SVG, um caminho por município com o código do IBGE como id, mais os centroides em JSON. A fonte é a API de malhas do IBGE, baixada em 2026-09-06 para `fonte/`; `construir.py` refaz tudo a partir dela e aceita outras unidades da federação.

## Técnico

- **Zero build.** Abrir o `.html` direto no navegador. Nenhum passo de compilação, nenhum gerenciador de pacotes.
- **Montserrat** servida de `assets/fonts/` sob a licença SIL Open Font, sem chamada externa.
- **Acessibilidade:** contraste medido par a par no `brand.json`, foco visível em tudo, `prefers-reduced-motion` respeitado, SVG de dado com `role`, `aria-label` e `<title>`, tabela sob toda figura de dado, piso de fonte de 11,5 px na página e 14 px efetivos no slide.
- **Navegadores:** os atuais. A régua usa consulta de container para o piso de fonte do gráfico; onde ela não existe, o gráfico volta a encolher e o resto continua igual.

## Sobre os arquivos gerados

`patterns/dado.html` nasceu de um gerador durante a construção do sistema e hoje se edita à mão, como as outras páginas do catálogo. `tokens/brand.json` e a base de `assets/mapas/` são gerados e têm o gerador ao lado (`gerar-brand.py` e `construir.py`), que rodam com o que está neste repositório.

---

*80 20 Marketing · São Paulo · Campo Grande · Cuiabá*
