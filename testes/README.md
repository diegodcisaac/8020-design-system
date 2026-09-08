# Testes

Uma pasta com um arquivo, e ele está errado de propósito.

`verificador-deve-reprovar.html` são quatro slides escritos para quebrar o máximo
de regras possível: cor fora da paleta, gradiente, sombra, raio, barra feita com
`div`, `fill` em texto de SVG, imagem sem `alt`, travessão, anglicismo, momentos
colados, título com o achado, tabela larga demais. Ele dispara 35 das 49 checagens
do verificador.

Não é exemplo e não é template. Não copie nada daqui: o que se copia está em
`../templates/` e em `../patterns/`.

Ele existe porque uma ferramenta que nunca reprova ninguém pode estar quebrada sem
que se perceba. Rodar, da raiz do repositório:

```bash
python3 verificar.py testes/verificador-deve-reprovar.html
```

A saída certa é reprovação, com 29 erros e 17 avisos. Se passar, o verificador
quebrou. O `conferir.py` roda essa checagem sozinho, e o sincronizador não deixa
subir nada enquanto ela não estiver de pé.
