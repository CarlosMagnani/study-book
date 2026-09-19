# Passo 4 — Análise local da transcrição

**Código explicado:** `src/study_book/analyze.py` (funções `ollama_complete` e `analyze`)  
**Teste explicado:** `tests/test_analyze.py` (classe `AnalyzeTest`)

## Contexto da mudança

O passo 3 definiu o formato validado de `analysis.json`, mas ainda sem
nenhum modelo. Este passo lê o texto de `transcript.json`, envia-o a um
modelo Ollama local (`qwen3:4b`) e valida a resposta contra o contrato
`Analysis`. Se a resposta vier malformada, a validação lança erro e nada é
salvo. O fluxo fica assim:

```text
transcript.json → texto → Ollama → JSON → Analysis (validação) → analysis.json
```

## Explicação de `analyze.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1 | A *docstring* descreve a responsabilidade do módulo: transformar `transcript.json` em `analysis.json` usando Ollama. A seta `->` aqui é só documentação da transformação. |
| 9–10 | Importam os dois contratos já definidos: `Analysis` (passo 3, para validar a resposta) e `Transcript` (passo 1, para ler o texto de entrada). |
| 12 | O comentário explica a decisão de teste: `complete` entra como argumento, então o teste passa uma função falsa e o modelo real só aparece nas execuções manuais. |
| 14–17 | `PROMPT = (...)` guarda o texto do pedido ao modelo. Os parênteses permitem quebrar uma string longa em várias linhas; Python junta as partes automaticamente. `{text}` é um espaço reservado preenchido depois com a transcrição. O pedido exige "JSON only" com as chaves do contrato. |
| 20 | `def ollama_complete(model: str = "qwen3:4b"):` declara a fábrica do conector real. `"qwen3:4b"` é o valor padrão do parâmetro, seguindo a recomendação do documento `free-local-stack.md`. |
| 21 | A importação fica dentro da função, como no passo 2: quem roda só os testes não precisa ter o pacote `ollama` instalado. O comentário é para o verificador Pyrefly ignorar a ausência na análise estática. |
| 23 | `Analysis.model_json_schema()` gera o esquema JSON do contrato. Esse esquema é passado ao Ollama para forçar a resposta a sair no formato certo (recurso de *structured outputs*). |
| 25–32 | `def complete(prompt: str) -> str:` declara uma função dentro da outra (*closure*): ela lembra `model` e `schema` mesmo depois de `ollama_complete` terminar. `ollama.chat(...)` envia uma mensagem de `role` `"user"`, com `format=schema` e `temperature` `0` (resposta mais repetível). `response.message.content or ""` devolve o texto, ou string vazia se vier nulo. |
| 34 | Devolve a função `complete` pronta para uso. Quem chama recebe um objeto chamável, não uma string. |
| 37 | `def analyze(transcript_path: str | Path, complete) -> Analysis:` declara a etapa: recebe o caminho do `transcript.json` e qualquer função que transforme pedido em JSON (a real ou uma falsa). |
| 38–39 | `Path(transcript_path)` normaliza o caminho. `Transcript.load(...).text` lê o JSON salvo no passo 2 e extrai só o texto corrido para enviar ao modelo. |
| 40 | `PROMPT.format(text=text)` insere a transcrição no pedido. `complete(...)` chama o modelo e `Analysis.model_validate_json(...)` valida a resposta na hora. Se falhar, lança `ValidationError` e a linha 41 nunca executa — por isso saída inválida nunca é salva. |
| 41–42 | `transcript_path.parent / "analysis.json"` monta o caminho na mesma pasta do vídeo. `save(...)` grava o JSON validado e a função devolve o objeto para uso imediato. |

## Por que o modelo é injetado?

Chamar o Ollama de verdade é lento e exige serviço rodando. O teste
verifica o que pertence a este projeto — montar o pedido com o texto,
validar a resposta e gravar o arquivo — usando uma função falsa que devolve
JSON controlado. Um segundo caso passa JSON inválido e prova que nada é
salvo.

## Explicação de `test_analyze.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1–8 | Importam padrão, `pydantic` (para `ValidationError`), a função sob teste e os contratos usados para montar a entrada e conferir a saída. |
| 11–16 | `make_transcript(path)` é uma função auxiliar (*helper*): cria um `Transcript` pequeno e salva no caminho dado. Evita repetir a montagem nos dois testes. `Segment(...)` constrói um trecho com início, fim e texto. |
| 19–20 | Declara a classe de teste e o primeiro caso. `complete(prompt)` é a função falsa: `assert` confere que o texto da transcrição chegou ao pedido e ela devolve um JSON válido fixo. |
| 22–29 | Cria a pasta temporária do vídeo, salva a transcrição de entrada, chama `analyze(...)` e confere o tema e que `analysis.json` lido de volta é igual ao devolvido. |
| 31–38 | O segundo caso passa um JSON sem `summary`. `assertRaises` espera `ValidationError` e `assertFalse(... .exists())` prova que nenhum arquivo foi criado. |

## Como executar este teste

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_analyze -v
```

## Limite atual

O resumo sai no idioma que o modelo escolher (no vídeo real, saiu em
inglês a partir de transcrição em português). Tradução automática está fora
do escopo do PRD; se um dia for preciso forçar o idioma, isso entra no texto
de `PROMPT`.
