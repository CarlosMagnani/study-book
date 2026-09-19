# Passo 6 — Exemplo de ponta a ponta

**Código executado:** nenhum arquivo novo; os três comandos prontos, nesta ordem, sobre `downloads/DdbtpWSRhWJ`

## Contexto

Com as etapas individuais funcionando, este passo roda o pipeline inteiro
sobre um vídeo real já baixado e inspeciona cada artefato à mão. O ingest
não precisou ser repetido: `audio.m4a` e `audio.info.json` já existiam da
execução original, o que também prova a história 9 do PRD (reexecutar uma
etapa sem baixar de novo).

## Comandos executados

```bash
PYTHONPATH=src .venv/bin/python -m study_book.transcribe downloads/DdbtpWSRhWJ
PYTHONPATH=src .venv/bin/python -m study_book.analyze downloads/DdbtpWSRhWJ
```

Ambos terminaram com saída `0` e imprimiram o caminho do arquivo gerado.
Antes disso, os caminhos de erro foram verificados à parte: pasta sem
`audio.m4a` responde "run the ingest step first"; pasta sem
`transcript.json` responde "run the transcribe step first".

## Artefatos inspecionados

| Arquivo | O que foi conferido |
| --- | --- |
| `audio.info.json` | `id` igual a `DdbtpWSRhWJ`; `title` indica vídeo de `marcelogaldinobjj`. Prova a origem do material. |
| `audio.m4a` | Existe, com ~500 KB. É a entrada da transcrição. |
| `transcript.json` | Carrega via `Transcript.load`: `source_id` correto, idioma `pt`, 10 segmentos com início/fim (primeiro de 0.0 a 7.0) e 875 caracteres de texto. |
| `analysis.json` | Carrega via `Analysis.load`: tema ("Brazilian Jiu-Jitsu Guard Technique: Armlock Application"), resumo e 3 pontos principais, coerentes com a transcrição. |

## Dependências de ambiente instaladas neste passo

| Item | Como |
| --- | --- |
| Pacote `ollama` (cliente Python) | `.venv/bin/python -m pip install ollama` (registrado em `requirements.txt`) |
| Binário `ollama` | Baixado do GitHub releases (`v0.34.2`, formato `.tar.zst`) para `~/.ollama-dist`, sem `sudo`; servido com `ollama serve` |
| Modelo `qwen3:4b` | `ollama pull qwen3:4b` (~2,5 GB) |

## Limite atual

O pipeline cobre conteúdo falado. Se um vídeo futuro depender de material
visual (slides, demonstrações não narradas, texto na tela), o PRD prevê
avaliar análise de imagem — fora deste marco.
