# Passo 8 — Interface web de prova de conceito

**Código explicado:** `src/study_book/web.py` e `src/study_book/web.html`  
**Teste explicado:** `tests/test_web.py`

## Contexto da mudança

Até o passo 7, usar o projeto exigia três comandos no terminal e abrir os
arquivos JSON à mão. Este passo adiciona uma página local, só para provar a
ideia (POC): você cola a URL de um reel, a página roda as três etapas em
sequência e mostra o tema, o resumo, os pontos principais e a transcrição.

O PRD lista "Web UI" como fora do escopo do primeiro marco; esta página é
um experimento por cima do pipeline, não uma mudança nele. Nenhuma etapa foi
alterada e nenhuma dependência nova foi instalada: o servidor usa apenas o
módulo padrão `http.server`.

```text
navegador ──GET /──────────────► web.html
          ──GET /api/videos────► lista de downloads/<id> com seus JSONs
          ──POST /api/ingest───► ingest.download      → {"id": ...}
          ──POST /api/transcribe► transcribe.transcribe → {"id": ...}
          ──POST /api/analyze──► analyze.analyze       → {"id": ...}
```

Para abrir:

```bash
PYTHONPATH=src .venv/bin/python -m study_book.web
# depois abra http://127.0.0.1:8000
```

## Explicação de `web.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1 | A *docstring* descreve o módulo: uma página local que roda as três etapas pelo navegador. |
| 3 | `from __future__ import annotations` faz o Python tratar as anotações de tipo como texto, permitindo escrever `list[str] | None` sem custo em tempo de execução. |
| 5–8 | Importações da biblioteca padrão: `argparse` (argumentos do comando), `json` (ler e escrever JSON), `BaseHTTPRequestHandler` e `ThreadingHTTPServer` (servidor HTTP) e `Path` (caminhos de arquivo). |
| 10 | `from study_book import analyze, ingest, transcribe` importa os três módulos das etapas. Importar o módulo inteiro (e não só a função) deixa as chamadas legíveis: `ingest.download(...)`. |
| 12 | O comentário registra a decisão: sem framework, e a função `run` é injetada para os testes usarem uma versão falsa. |
| 14 | `Path(__file__)` é o caminho deste arquivo; `.with_name("web.html")` troca só o nome, apontando para o HTML que mora na mesma pasta. |
| 17 | `def video_dir(downloads: Path, video_id: str) -> Path:` transforma um id recebido do navegador na pasta do vídeo. |
| 18–19 | `{p.name for p in downloads.glob("*") if p.is_dir()}` é uma *set comprehension*: monta o conjunto dos nomes das pastas que existem em `downloads`. `not in` verifica se o id está nesse conjunto; se não estiver, `raise LookupError(...)` interrompe com erro. Essa é a proteção de segurança: um id como `..` nunca aparece na listagem, então ninguém consegue apontar para fora de `downloads`. |
| 20 | Só depois da verificação o caminho é montado com o operador `/` de `Path`. |
| 23–24 | `read_json` usa uma expressão condicional (`A if condição else B`): devolve o JSON lido se o arquivo existe, ou `None` se não existe. |
| 27 | `describe(folder)` monta o resumo de um vídeo que a página vai exibir. |
| 28 | `read_json(...) or {}` troca `None` por um dicionário vazio, para a linha 31 poder chamar `.get` sem erro. |
| 29–34 | Devolve um dicionário com o id (nome da pasta), o título vindo dos metadados (`info.get("title", "")` devolve `""` se a chave faltar), a transcrição e a análise. Os dois últimos ficam `None` quando a etapa ainda não rodou — é assim que a página sabe em que ponto o vídeo está. |
| 37 | `run_stage(stage, body, downloads)` executa uma etapa pelo nome e devolve o id do vídeo. |
| 38–39 | Na etapa `ingest` ainda não existe pasta, então ela é tratada primeiro. `ingest.instagram_url(body["url"])` valida a URL (lança erro se não for do Instagram) e `ingest.download(...)` baixa; `.name` extrai o id da pasta devolvida. |
| 40 | Para as outras etapas, o id recebido passa por `video_dir`, a verificação das linhas 17–20. |
| 41–44 | `if`/`elif` escolhe a etapa e chama a mesma função que o comando de terminal chama, com o conector real (`default_model()` do Whisper ou `ollama_complete()`). |
| 45–46 | `else: raise LookupError(...)` recusa qualquer nome de etapa desconhecido. |
| 47 | Devolve o id para a página saber qual vídeo mostrar. |
| 50 | `make_handler(downloads, run=run_stage)` é uma fábrica: recebe a pasta e a função que roda etapas e devolve uma classe. `run=run_stage` é o valor padrão; o teste passa outra função no lugar. |
| 51 | `class Handler(BaseHTTPRequestHandler):` cria a classe dentro da função (*closure*), então os métodos enxergam `downloads` e `run`. O `http.server` cria um objeto dessa classe para cada requisição. |
| 52 | `reply(self, status, body, content_type="application/json")` é um auxiliar para não repetir as quatro chamadas de resposta. `body: bytes` indica que o corpo já chega codificado. |
| 53–57 | `send_response` escreve o código HTTP (200, 404, 500); `send_header` adiciona cabeçalhos — o tipo do conteúdo e o tamanho em bytes (`str(len(body))`, pois cabeçalhos são texto); `end_headers` encerra os cabeçalhos; `self.wfile.write(body)` envia o corpo. |
| 59 | `do_GET` é o nome que o `http.server` procura para atender requisições GET. |
| 60–61 | `self.path` é o caminho pedido. Em `/`, envia o HTML lido em bytes (`read_bytes`) com o tipo `text/html`. |
| 62–64 | Em `/api/videos`, uma *list comprehension* chama `describe` para cada pasta de `downloads`, em ordem alfabética (`sorted`). `json.dumps(videos)` vira texto e `.encode()` vira bytes. |
| 65–66 | Qualquer outro caminho recebe 404. O `b` antes das aspas cria bytes diretamente. |
| 68 | `do_POST` atende requisições POST, usadas para rodar etapas. |
| 69 | `try:` protege todo o bloco: qualquer falha vira uma resposta de erro em vez de derrubar a conexão. |
| 70 | `self.headers["Content-Length"]` diz quantos bytes o navegador enviou; `int(...)` converte, `self.rfile.read(...)` lê exatamente essa quantidade e `json.loads` transforma em dicionário. |
| 71 | `self.path.removeprefix("/api/")` tira o prefixo e sobra o nome da etapa (`ingest`, `transcribe` ou `analyze`), que é passado a `run`. |
| 72 | Em caso de sucesso, responde 200 com `{"id": ...}`. |
| 73–74 | `except Exception as error:` captura qualquer erro (URL inválida, vídeo desconhecido, Ollama desligado) e responde 500 com a mensagem em `str(error)`, que a página mostra ao usuário. |
| 76 | A fábrica devolve a classe pronta. |
| 79–82 | `main` segue o padrão dos outros comandos. `--port` é um argumento opcional (começa com `--`), convertido para inteiro, com padrão 8000. |
| 83 | `ThreadingHTTPServer(("127.0.0.1", port), ...)` cria o servidor. O endereço `127.0.0.1` aceita conexões só deste computador. "Threading" significa uma *thread* por requisição: a página continua respondendo enquanto uma transcrição demorada roda. |
| 84 | Imprime o endereço para abrir no navegador. |
| 85–88 | `serve_forever()` atende requisições até ser interrompido. `except KeyboardInterrupt: pass` faz o Ctrl+C encerrar em silêncio, sem mostrar um erro. |
| 89 | `return 0` sinaliza sucesso ao sistema. |
| 92–93 | Executa `main` só quando o módulo é chamado como programa (`python -m study_book.web`). |

## Explicação de `web.html`, por bloco

O arquivo não é Python; a explicação segue os blocos, de cima para baixo.

| Bloco | Explicação |
| --- | --- |
| `<style>` | As cores ficam em variáveis CSS (`--bg`, `--accent`...) definidas em `:root`. O bloco `@media (prefers-color-scheme: dark)` redefine as mesmas variáveis para o tema escuro do sistema. `.layout` usa `grid` com duas colunas e vira uma só em telas estreitas. As classes `running`, `done` e `failed` pintam o indicador de cada etapa. |
| `<form id="form">` | O campo de URL (`type="url"` e `required` fazem o navegador validar antes de enviar) e o botão "Run pipeline". |
| `<ol id="stages">` | Os três indicadores de etapa. Cada `<li>` tem um `id` (`stage-ingest`...) para o JavaScript mudar sua classe. |
| `#error`, `#list`, `#detail` | Elementos vazios que o JavaScript preenche: mensagem de erro, lista de vídeos e painel do vídeo selecionado. |
| `STAGES`, `$`, `videos`, `selected`, `busy` | O estado da página: a ordem das etapas, um atalho para `document.getElementById`, os vídeos recebidos, o id selecionado e uma trava para não rodar duas execuções ao mesmo tempo. |
| `el(tag, text, parent)` | Cria um elemento, define o texto com `textContent` e o anexa ao pai. Usar `textContent` (e nunca `innerHTML`) garante que texto vindo do modelo ou do Instagram apareça como texto, sem ser interpretado como HTML. |
| `clock(seconds)` | Converte segundos em `m:ss`; `padStart(2, "0")` completa com zero à esquerda. |
| `api(path, body)` | Chama o servidor com `fetch`. Com `body`, envia um POST em JSON; sem ele, um GET. Se a resposta não for de sucesso (`!response.ok`), lança um erro com a mensagem vinda do servidor. `async`/`await` permitem esperar a resposta sem travar a página. |
| `runStages(stages, body)` | O coração da página. Para cada etapa: marca como `running`, chama `/api/<etapa>`, guarda o id devolvido, marca como `done` e recarrega a lista. O id devolvido por uma etapa vira o corpo da próxima — por isso o ingest recebe `{url}` e as demais recebem `{id}`. Se algo falhar, o `catch` marca a etapa como `failed` e mostra o erro. |
| `refresh()` | Busca `/api/videos`, mantém a seleção se ela ainda existe e redesenha lista e painel. |
| `renderList()` | Desenha um botão por vídeo com o tema (ou título, ou id) e o estado: `audio only`, `transcribed` ou `analyzed`. `?.` (encadeamento opcional) evita erro quando `analysis` é nulo. |
| `renderDetail(video)` | Desenha o tema, o resumo, os pontos principais, os momentos e a transcrição com o tempo de cada trecho. No fim, cria os botões que rodam uma etapa isolada; "Analyze" só aparece quando já existe transcrição. |
| `$("form").onsubmit` | `preventDefault()` impede o navegador de recarregar a página; em seguida roda as três etapas com a URL digitada. |
| `refresh()` final | Carrega os vídeos já existentes assim que a página abre. |

## Por que a função `run` é injetada?

Rodar as etapas de verdade exige rede, o modelo Whisper e o Ollama. O teste
verifica o que pertence a este passo — rotas, formato das respostas e
tratamento de erro — passando uma função falsa a `make_handler`, do mesmo
jeito que os passos 2 e 4 injetam o modelo.

## Explicação de `test_web.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1–11 | Importações: `threading` para rodar o servidor em paralelo ao teste, `urllib.request` e `urllib.error` para fazer requisições HTTP reais, e as funções sob teste. |
| 14–17 | `fake_run` é a função falsa. Para `analyze` ela lança `RuntimeError`, simulando o Ollama desligado; para as outras devolve um texto com a etapa e o id, o que prova que os dois chegaram até ela. |
| 20–22 | `setUp` roda antes de cada teste. `tempfile.TemporaryDirectory()` cria uma pasta temporária e `addCleanup` agenda sua remoção ao fim do teste. |
| 23–30 | Monta um vídeo de exemplo: a pasta, um `audio.info.json` com título e um `transcript.json` salvo pelo contrato do passo 1. Não há `analysis.json`, de propósito. |
| 32–33 | Cria a classe com a função falsa. `handler.log_message = lambda *args: None` substitui o registro de requisições por uma função que não faz nada, para não poluir a saída dos testes. |
| 34–36 | Porta `0` pede ao sistema qualquer porta livre. Os `addCleanup` rodam em ordem inversa: primeiro `shutdown` (para o laço), depois `server_close` (libera a porta). |
| 37 | `threading.Thread(target=..., daemon=True).start()` roda `serve_forever` em outra *thread*; `daemon=True` não deixa essa *thread* segurar o processo aberto. |
| 38 | `server_port` é a porta que o sistema escolheu; com ela monta o endereço base. |
| 40–42 | `post` é um auxiliar: passar `data=` a `Request` transforma a requisição em POST. `json.load` lê a resposta. |
| 44–46 | Confere que `/` devolve a página, procurando o título. |
| 48–53 | `(video,) = ...` desempacota uma lista de exatamente um item (falha se vierem zero ou dois). Confere id, título, idioma da transcrição e que `analysis` é `None`. |
| 55–57 | Confere que o POST repassa a etapa do caminho e o corpo para `run`. |
| 59–63 | A etapa que falha deve responder 500. `assertRaises(...) as caught` guarda o erro; `caught.exception.code` é o código HTTP e o corpo traz a mensagem original. |
| 65–68 | Chama `run_stage` real com ids inválidos (`..`, inexistente e vazio) e espera `LookupError` — a proteção das linhas 17–20 de `web.py`. O erro acontece antes de qualquer modelo ser carregado. |

## Como executar este teste

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_web -v
```

## Limite atual

É uma prova de conceito para uso local por uma pessoa:

- Cada etapa segura a requisição até terminar; não há fila nem barra de
  progresso real, só o indicador "rodando".
- O modelo Whisper é carregado de novo a cada transcrição.
- Não há autenticação; por isso o servidor escuta apenas em `127.0.0.1`.
- O servidor precisa ser iniciado a partir da raiz do repositório, porque
  `downloads/` é relativo à pasta atual.
