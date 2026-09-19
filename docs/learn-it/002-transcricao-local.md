# Passo 2 — Transcrição local

**Código explicado:** `src/study_book/transcribe.py`  
**Teste explicado:** `tests/test_transcribe.py`

## Contexto da mudança

O passo 1 definiu e salvou o formato de `transcript.json`, mas ainda não
produzia texto a partir de áudio. Este passo recebe o arquivo `audio.m4a`,
envia-o para um modelo Faster-Whisper e transforma os segmentos retornados no
contrato `Transcript` já definido.

O arquivo final é salvo na mesma pasta do áudio. O fluxo fica assim:

```text
audio.m4a → modelo Faster-Whisper → objetos Segment → Transcript → transcript.json
```

## Explicação de `transcribe.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1 | A *docstring* descreve a responsabilidade do módulo. `->` aqui é texto de documentação: indica a transformação de áudio para JSON. |
| 3 | Adia a resolução das anotações de tipo. É a mesma sintaxe explicada na nota 001. |
| 5 | Importa `Path`, o tipo usado para trabalhar com caminhos de arquivo. |
| 7 | Importa `Segment` e `Transcript` do contrato do passo 1. Assim este módulo reutiliza o formato já decidido, em vez de criar outro JSON diferente. |
| 9 | O comentário explica uma decisão de teste: `model` entra como argumento. O teste pode então passar um modelo falso, sem baixar um modelo real nem processar áudio. |
| 12 | `def default_model():` declara uma função sem parâmetros. Ela concentra a criação do modelo real, mas ainda não executa nada até ser chamada. |
| 13 | Este comentário é entendido pelo verificador Pyrefly. Ele ignora a ausência da dependência durante análise estática; ao executar com Faster-Whisper instalado, a importação continua normal. |
| 14 | A importação fica dentro da função. Isso significa que quem só executa os testes não precisa carregar `faster_whisper` ao importar o módulo. |
| 16 | `return` devolve o modelo. `WhisperModel("small", ...)` chama a classe para criar um objeto. `device="cpu"` escolhe CPU e `compute_type="int8"` pede uma representação mais leve para CPU. |
| 19 | `audio: str | Path` aceita uma string ou `Path`; `model` recebe qualquer objeto que ofereça o método `transcribe`; `-> Transcript` documenta o retorno. |
| 20 | `Path(audio)` normaliza a entrada. Depois desta linha, `audio` sempre é um `Path`, mesmo que a função tenha recebido uma string. |
| 21 | A vírgula faz *desempacotamento* de uma tupla: o método retorna dois valores. `segments` recebe os segmentos e `info` recebe informações como idioma. `str(audio)` converte o caminho para texto porque a biblioteca aceita texto. `beam_size=5` é um argumento nomeado que controla a busca do modelo. |
| 22 | Esta é uma *list comprehension*: `[resultado for item in coleção]`. Para cada segmento `s` retornado pelo modelo, ela cria um `Segment`. `s.text.strip()` remove espaços no início e no fim do texto. Percorrer `segments` também consome o iterador devolvido por Faster-Whisper. |
| 23 | `t = Transcript(` começa a criação da transcrição final e guarda o objeto na variável curta `t`. |
| 24 | `audio.parent` é a pasta que contém o áudio; `.name` é apenas o último nome dessa pasta. Neste projeto esse nome é o identificador do vídeo. |
| 25 | `getattr(info, "language", "pt")` lê o atributo `language` de `info`. Se o atributo não existir, usa `"pt"` como padrão. |
| 26 | `" ".join(...)` une vários textos colocando um espaço entre eles. `s.text for s in segs` é uma *generator expression*: produz um texto por vez para `join`, sem montar outra lista. |
| 27 | Passa a lista de segmentos criada na linha 22 para o campo `segments` do contrato. |
| 28 | Fecha a chamada de `Transcript(...)`. A vírgula final é válida em Python e facilita acrescentar ou remover campos em várias linhas. |
| 29 | `audio.parent / "transcript.json"` usa o operador `/` de `Path` para montar um caminho. `t.save(...)` chama o método do passo 1 e grava o JSON na pasta do vídeo. |
| 30 | Devolve a mesma transcrição que acabou de ser salva. Isso permite que outro código use o resultado sem precisar ler o arquivo novamente. |

## Por que existe um teste com modelo falso?

O Faster-Whisper processa áudio real e pode ser lento. O teste verifica a
integração que pertence a este projeto — criação dos segmentos, texto unido,
idioma, caminho de saída e JSON salvo — sem depender de rede, GPU ou modelo
baixado.

## Explicação de `test_transcribe.py`, linha por linha

| Linhas | Explicação |
| --- | --- |
| 1–4 | Importam módulos padrão. `tempfile` cria uma pasta temporária; `unittest` fornece testes; `SimpleNamespace` cria objetos simples com atributos, úteis para imitar respostas do modelo. |
| 6–7 | Importam a função sob teste e o contrato que será usado para confirmar o arquivo salvo. |
| 10 | `class StubModel:` declara um substituto pequeno para o modelo real. *Stub* é um objeto falso com uma resposta controlada. |
| 11 | O método tem o mesmo nome esperado pelo código real: `transcribe`. O valor padrão `beam_size=5` permite conferir que a função usa o argumento previsto. |
| 12 | `assert` interrompe o teste se o caminho não terminar em `audio.m4a`. É uma verificação simples do argumento entregue ao modelo. |
| 13–16 | A lista contém dois segmentos falsos. `SimpleNamespace(start=..., ...)` permite acessar os valores com ponto, como `s.start`, exatamente como no objeto real. Os espaços extras também verificam o `.strip()` da linha 22 do código. |
| 17 | Devolve os dois valores que o código de produção espera: segmentos e informações. |
| 20 | Cria uma classe de teste herdando de `unittest.TestCase`. Os parênteses indicam herança. |
| 21 | Métodos cujo nome começa com `test_` são executados pelo `unittest`. `-> None` documenta que ele não retorna valor. |
| 22 | `with ... as d:` cria uma pasta temporária e garante que ela seja removida ao terminar o bloco, mesmo se o teste falhar. |
| 23 | Monta um caminho de exemplo usando `/` entre objetos `Path`. |
| 24 | Cria a pasta do identificador do vídeo. |
| 25 | Cria um arquivo vazio chamado `audio.m4a`. O conteúdo não importa, pois o stub não o lê. |
| 26 | Chama a função real com o caminho e uma instância do modelo falso. O retorno é guardado em `t`. |
| 27–29 | `self.assertEqual(valor_atual, valor_esperado)` compara identificador, idioma e texto final. O texto esperado prova que os espaços extras foram removidos e os segmentos unidos. |
| 30 | Lê o JSON salvo com `Transcript.load(...)` e compara o resultado com `t`. Isso prova que o arquivo foi escrito no local esperado e pode ser lido de volta. |
| 33–34 | Este padrão permite executar o arquivo diretamente (`python ...`) e iniciar o `unittest`. Ao importar o arquivo em outra situação, esse bloco não roda. |

## Como executar este teste

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.test_transcribe -v
```

## Limite atual

`transcribe()` já funciona com qualquer objeto que tenha `transcribe`, mas a
interface de linha de comando ainda não chama `default_model()`. Isso será a
próxima etapa: receber um identificador ou caminho de áudio, verificar os
arquivos necessários e acionar a transcrição real.
