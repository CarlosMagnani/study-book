# Passo 3 — Contrato de análise

**Código explicado:** `src/study_book/analysis.py`  
**Teste explicado:** `tests/test_analysis.py`

## Contexto da mudança

O passo 2 produz `transcript.json` com texto e tempos. O passo 4 vai enviar
esse texto a um modelo local (Ollama) e pedir de volta um tema, um resumo e
pontos principais. Antes de conectar o modelo, este passo define o formato
exato dessa resposta e prova duas coisas: dado válido pode ser salvo e lido
de volta; dado malformado falha com erro claro, em vez de ser salvo.

A validação usa Pydantic, a mesma biblioteca que o passo 4 vai usar para
conferir a saída do modelo antes de gravar `analysis.json`. O fluxo fica
assim:

```text
resposta do modelo → Analysis (validação) → analysis.json
```

## Explicação de `analysis.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1 | A *docstring* descreve a responsabilidade do módulo: o formato validado de tema, resumo e pontos principais. |
| 3 | Adia a resolução das anotações de tipo. É a mesma sintaxe explicada na nota 001. |
| 5 | Importa `Path`, o tipo usado para trabalhar com caminhos de arquivo. |
| 7 | Importa `BaseModel` e `Field` do Pydantic. `BaseModel` é a classe base que valida os campos automaticamente; `Field` permite regras extras, como tamanho mínimo. |
| 9 | O comentário registra uma simplificação deliberada: `timestamps` continua uma lista opcional simples. Intervalos mais ricos só entram se a saída do modelo no passo 4 exigir. |
| 12 | `class SourceTimestamp(BaseModel):` declara um modelo Pydantic por herança. Os parênteses indicam que `SourceTimestamp` é um tipo de `BaseModel` e ganha a validação dele. |
| 13–15 | Três campos com anotações de tipo: `start` e `end` são números (`float`) com o tempo em segundos; `label` é texto com valor padrão `""`, então é opcional na entrada. Se `start` chegar como texto, o Pydantic tenta converter; se não conseguir, rejeita. |
| 18 | `class Analysis(BaseModel):` declara o contrato principal da análise. |
| 19 | `topic: str = Field(min_length=1)` exige um texto não vazio. `Field(...)` configura o campo; `min_length=1` rejeita string vazia, que seria um tema inútil vindo do modelo. |
| 20 | A mesma regra para `summary`: resumo vazio falha na validação. |
| 21 | `key_points: list[str] = []` é uma lista de textos com padrão vazio. Lista vazia é aceita: um resumo sem pontos principais é fraco, mas não é dado malformado. |
| 22 | `timestamps: list[SourceTimestamp] = []` é uma lista de `SourceTimestamp`, também opcional. Cada item da lista é validado contra o modelo da linha 12. |
| 24–25 | `def save(...)` recebe `self` (a própria análise) e um caminho (`str` ou `Path`). `model_dump_json(indent=2)` converte o modelo em texto JSON indentado; `write_text(...)` grava o arquivo. O `+ "\n"` termina o arquivo com quebra de linha. |
| 27–29 | `@classmethod` indica um método da classe, não do objeto. `load` lê o texto do arquivo e `model_validate_json(...)` reconstrói e valida um `Analysis`. `cls` aqui é `Analysis`, então o retorno já é tipado. |

## Por que validar antes de conectar o modelo?

Modelos de linguagem às vezes devolvem JSON incompleto ou com tipos
trocados. Com o contrato pronto, o passo 4 só precisa de duas linhas de
lógica: tentar validar e, se falhar, informar o erro em vez de salvar. O
teste abaixo prova exatamente esse comportamento.

## Explicação de `test_analysis.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1–6 | Importam módulos padrão e do projeto. `pydantic` entra para referenciar `ValidationError`, o erro lançado quando a validação falha. |
| 9 | Cria a classe de teste herdando de `unittest.TestCase`. |
| 10 | Métodos cujo nome começa com `test_` são executados pelo `unittest`. |
| 11–17 | Monta um `Analysis` válido, com tema, resumo, dois pontos principais e um carimbo de tempo passado como dicionário — o Pydantic converte o dicionário em `SourceTimestamp` sozinho. |
| 18–21 | `TemporaryDirectory` cria uma pasta temporária que se apaga sozinha. O teste salva `analysis.json` nela e confere que ler de volta devolve um objeto igual. Isso prova que dado válido pode ser salvo. |
| 24–28 | `assertRaises(...)` espera que o bloco lance aquele erro. O primeiro caso omite `summary` (campo obrigatório); o segundo passa `key_points` como texto em vez de lista. Ambos devem lançar `pydantic.ValidationError`, provando que dado malformado falha com erro claro. |
| 31–32 | Este padrão permite executar o arquivo diretamente e iniciar o `unittest`. Ao importar o arquivo, esse bloco não roda. |

## Como executar este teste

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_analysis -v
```

## Limite atual

O contrato aceita qualquer texto não vazio como `topic`; não existe ainda
uma lista fixa de temas com `other` como alternativa. Se o passo 4 mostrar
temas inconsistentes vindos do modelo, esse é o próximo aperto: validar o
tema contra uma lista permitida.
