# Passo 5 — Comandos das etapas com proteções

**Código explicado:** `main` em `src/study_book/transcribe.py` (linhas 35–48) e em `src/study_book/analyze.py` (linhas 45–58)  
**Teste explicado:** `TranscribeCommandTest` em `tests/test_transcribe.py`, `AnalyzeCommandTest` em `tests/test_analyze.py`

## Contexto da mudança

Até o passo 4, cada etapa só funcionava chamada por código. Este passo
expõe transcrição e análise como comandos independentes, cada um lendo o
artefato da etapa anterior e verificando se ele existe. Se faltar, o comando
avisa qual etapa deve rodar antes, em vez de quebrar com erro técnico. O
ingest continua sendo o `app.py` da raiz (transitório). O fluxo fica assim:

```text
python -m study_book.transcribe downloads/<id>  → transcript.json
python -m study_book.analyze downloads/<id>     → analysis.json
```

## Explicação de `main`, linha por linha (vale para os dois módulos)

| Linhas | Explicação |
| --- | --- |
| 35/45 | `def main(argv: list[str] | None = None, model=None/complete=None):` declara o comando. `argv` permite passar argumentos no teste; valendo `None`, o `argparse` lê a linha de comando de verdade. O segundo parâmetro injeta o modelo falso nos testes. |
| 36/46 | `argparse.ArgumentParser(...)` cria o interpretador de argumentos; `description` aparece na ajuda (`--help`). É um módulo padrão, sem dependência nova. |
| 37/47 | `add_argument("dir", type=Path, ...)` declara um argumento posicional: a pasta do vídeo. `type=Path` já converte o texto em `Path` automaticamente. |
| 38/48 | `parser.parse_args(argv).dir / "audio.m4a"` lê o argumento e monta o caminho do artefato esperado da etapa anterior (`audio.m4a` ou `transcript.json`). |
| 39–41/49–51 | `if not ... .exists():` é a proteção. `print(..., file=sys.stderr)` escreve o erro na saída de erro, e `return 1` sinaliza falha ao sistema. A mensagem diz qual etapa anterior deve rodar ("ingest" ou "transcribe"). |
| 42/52 | Chama a função da etapa com o conector real quando o teste não injetou um falso (`model or default_model()`). O `or` aqui significa "use o da esquerda, ou o da direita se for nulo". |
| 43/53 | `print(f"Wrote ...")` confirma o arquivo gerado. A *f-string* (texto com `f` antes das aspas) insere o caminho entre chaves. |
| 44/54 | `return 0` sinaliza sucesso ao sistema. |
| 47–48/57–58 | `if __name__ == "__main__":` só executa na chamada como programa (`python -m ...`). `raise SystemExit(main())` transforma o código de retorno em saída do processo. |

## Por que testar o comando?

A história 8 do PRD pede mensagens úteis quando falta a entrada esperada.
Os testes provam os dois lados: pasta sem `audio.m4a` retorna 1 (e a
mensagem cita o ingest); pasta com o artefato e conector falso retorna 0 e
o arquivo aparece. Nenhum teste baixa modelo nem processa áudio real.

## Como executar estes testes

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_transcribe tests.test_analyze -v
```

## Limite atual

Os três comandos ainda são programas separados (`app.py`, `transcribe`,
`analyze`); não existe um comando único que rode tudo. Isso é proposital:
o PRD adia o comando combinado até as etapas individuais estarem
compreendidas e funcionando.
