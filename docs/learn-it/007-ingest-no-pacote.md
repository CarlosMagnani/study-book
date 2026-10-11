# Passo 7 — Ingest dentro do pacote

**Código explicado:** `src/study_book/ingest.py` (antes `app.py`, na raiz)  
**Teste explicado:** `tests/test_ingest.py` (antes `tests/test_app.py`)

## Contexto da mudança

O download do áudio ainda morava em `app.py`, na raiz do repositório, e toda
a lógica ficava dentro de `main`. Isso tinha dois problemas: o `AGENTS.md`
pede que o código da aplicação fique em `src/study_book/`, e nenhum outro
módulo conseguia pedir um download sem simular a linha de comando.

Este passo move o arquivo para o pacote e separa o download em uma função
própria, `download(url)`, que devolve a pasta do vídeo. O comportamento para
quem usa o terminal é o mesmo; só o comando muda:

```text
antes:  python app.py <url>
agora:  PYTHONPATH=src python -m study_book.ingest <url>
```

O passo 8 (interface web) depende dessa função.

## Explicação de `ingest.py`, linha por linha

Só as linhas novas ou alteradas são explicadas; `instagram_url` (linhas
10–14) não mudou.

| Linhas | Explicação |
| --- | --- |
| 1 | A *docstring* foi adicionada para dizer o que o módulo faz, no mesmo estilo dos outros: entrada à esquerda da seta, artefatos à direita. |
| 17 | `def download(url: str) -> Path:` declara a nova função. `url: str` é a anotação do parâmetro e `-> Path` informa que ela devolve um caminho (a pasta `downloads/<id>`). |
| 18–24 | O dicionário `options` é o mesmo de antes, apenas movido de `main` para cá. Ele configura o yt-dlp: melhor áudio disponível, nome do arquivo de saída, gravação do `audio.info.json` e conversão para M4A pelo FFmpeg. |
| 25–26 | `with yt_dlp.YoutubeDL(options) as ydl:` abre o baixador e garante que ele seja fechado ao sair do bloco. `extract_info(url, download=True)` baixa o áudio e devolve os metadados. |
| 27 | Antes havia um `print` aqui. Agora a função usa `return`: `ydl.prepare_filename(info)` calcula o nome do arquivo baixado e `.parent` pega a pasta dele. Devolver o valor, em vez de imprimir, é o que permite outro módulo usar o resultado. |
| 30–33 | `main` ficou só com a parte de linha de comando: cria o `ArgumentParser`, declara o argumento `url` (validado por `instagram_url`) e imprime o que `download` devolveu. `parser.parse_args().url` lê o argumento e a *f-string* insere a pasta no texto. |

## Explicação de `test_ingest.py`

| Linhas | Explicação |
| --- | --- |
| 4 | `from study_book.ingest import instagram_url` substitui `from app import instagram_url`. É a única linha alterada: o teste continua o mesmo, só aponta para o novo endereço do módulo. |

## Como executar este teste

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_ingest -v
```

## Limite atual

`download` grava sempre em `downloads/`, relativo à pasta de onde o comando
foi executado. Por isso todos os comandos devem ser rodados a partir da raiz
do repositório. A função também não tem teste próprio, porque testá-la de
verdade exigiria rede e uma URL real do Instagram.
