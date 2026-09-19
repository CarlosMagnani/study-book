# Passo 1 — Contrato da transcrição

**Código explicado:** `src/study_book/transcript.py`

## Contexto da mudança

Antes de chamar um modelo de transcrição, o projeto precisa decidir como vai
guardar o resultado. Este arquivo define um contrato simples: uma transcrição
tem o identificador do vídeo, idioma, texto completo e segmentos com início e
fim em segundos. Esse contrato é a ponte entre a futura etapa de transcrição e
a futura etapa de resumo.

O resultado será salvo como `transcript.json` ao lado do áudio do vídeo. Assim,
cada etapa pode ser executada, examinada e testada separadamente.

## Formato produzido

```json
{
  "source_id": "video-id",
  "language": "pt",
  "text": "Texto completo do vídeo.",
  "segments": [
    {"start": 0.0, "end": 2.4, "text": "Primeira frase."}
  ]
}
```

## Explicação linha por linha

| Linhas | Explicação |
| --- | --- |
| 1–6 | As aspas triplas criam uma *docstring*: um texto de documentação no início do módulo. Ela descreve o objetivo do arquivo e mostra o formato JSON esperado. `str`, `float` e `None` são tipos de valores. |
| 8 | `from __future__ import annotations` faz as anotações de tipo serem tratadas de forma adiada. Por isso `-> Transcript` pode aparecer dentro da própria classe sem precisar escrever `"Transcript"`. |
| 10 | `import json` carrega o módulo padrão do Python para transformar dicionários em JSON e JSON em dicionários. |
| 11 | `from ... import ...` importa apenas os nomes usados. `@dataclass` cria automaticamente um construtor; `asdict` transforma uma dataclass em dicionário. |
| 12 | `Path` representa caminhos de arquivos de forma orientada a objetos, por exemplo `Path("downloads/id/transcript.json")`. |
| 14 | Este comentário registra uma decisão: nesta primeira etapa usamos `dataclass`, que já existe no Python. Validação rígida com Pydantic fica para o contrato de análise, quando ela será necessária. |
| 17 | `@dataclass` é um *decorator*: o símbolo `@` aplica um comportamento extra à classe logo abaixo. Aqui ele cria, entre outras coisas, `Segment(start=..., end=..., text=...)`. |
| 18 | `class Segment:` declara um novo tipo chamado `Segment`. Ele representa uma parte falada do áudio. Os dois pontos iniciam o bloco da classe. |
| 19 | `start: float` declara o atributo `start`, esperado como número decimal. É o segundo em que o segmento começa. |
| 20 | `end: float` declara o segundo em que o segmento termina. |
| 21 | `text: str` declara o texto falado naquele intervalo. `str` significa texto. |
| 24–25 | Um segundo `@dataclass` cria o tipo `Transcript`, que agrupa todos os dados de uma transcrição. |
| 26 | `source_id: str` guarda o identificador do vídeo como texto. |
| 27 | `language: str | None` usa `|` para dizer “texto **ou** ausência de valor”. `None` é o valor especial de Python para “não informado”. |
| 28 | `text: str` guarda a transcrição completa em uma única string. |
| 29 | `segments: list[Segment]` diz que `segments` é uma lista (`list`) cujos itens são objetos `Segment`. Os colchetes indicam o tipo dos itens. |
| 31 | `def` começa uma função/método. `self` é o próprio objeto `Transcript` atual. `-> dict` documenta que o retorno será um dicionário. |
| 32 | `return` devolve um valor. `asdict(self)` percorre a transcrição e os segmentos, convertendo-os em dicionários normais que podem virar JSON. |
| 34 | `@classmethod` cria um método que trabalha com a classe, não com uma instância existente. Ele é usado para construir uma nova transcrição a partir de dados já lidos. |
| 35 | `cls` é a classe atual (`Transcript`). `d: dict` recebe um dicionário. O método promete retornar um `Transcript`. |
| 36 | `return cls(` cria e devolve uma nova instância. Usar `cls` em vez de escrever `Transcript` permite reutilizar o método em uma eventual subclasse. |
| 37 | `d["source_id"]` acessa uma chave obrigatória. Se ela não existir, Python mostra um erro; isso protege um dado essencial. |
| 38 | `d.get("language")` acessa uma chave opcional. Se ela não existir, devolve `None` em vez de lançar erro. |
| 39 | `d["text"]` lê o texto completo, que também é obrigatório. |
| 40 | Esta é uma *list comprehension*: `[expressão for item in coleção]`. Para cada dicionário `s` em `d["segments"]`, `Segment(**s)` cria um segmento. `**s` desempacota chaves como argumentos nomeados: `{"start": 0}` vira `start=0`. |
| 43 | `path: str | Path` aceita texto ou um objeto `Path`. `-> None` indica que o método executa uma ação, mas não devolve um valor útil. |
| 44 | `Path(path)` normaliza o caminho. `.write_text(...)` escreve texto no arquivo. `json.dumps(...)` converte o dicionário em JSON; `indent=2` deixa o arquivo legível; `+ "\\n"` adiciona uma quebra de linha final. |
| 46–47 | Outro `@classmethod`, agora para ler uma transcrição salva. Ele recebe o caminho e retorna um novo objeto `Transcript`. |
| 48 | A execução ocorre de dentro para fora: `read_text()` lê o arquivo; `json.loads(...)` converte JSON em dicionário; `cls.from_dict(...)` converte o dicionário em `Transcript`. |

## Limite atual

`save()` espera que a pasta do vídeo já exista. Isso é aceitável neste passo,
porque a etapa de ingestão cria a pasta. Na etapa de comando de transcrição,
vamos apresentar um erro claro caso o áudio ou a pasta esperados não existam.
