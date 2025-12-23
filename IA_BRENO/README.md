# IA_BRENO

Esta é a IA Ultra Inteligente criada para Breno.

## Configuração

1. Abra o arquivo `config.py`.
2. Configure sua `API_KEY` e `API_BASE_URL`.
   - Para usar o modelo `gpt-oss-120b:free` (ou qualquer outro), recomendo usar um provedor como OpenRouter ou uma API local (Ollama/LM Studio).
   - Exemplo OpenRouter:
     - `API_BASE_URL = "https://openrouter.ai/api/v1"`
     - `API_KEY = "sk-or-..."`
     - `MODEL_NAME = "google/gemini-pro-1.5" ` (ou o nome exato do modelo desejado)

## Como Iniciar

1. Execute o arquivo `run.bat` (no Windows).
2. Quando solicitado, digite o nome de usuário: `Breno`.

## Funcionalidades

- **Identidade Exclusiva**: Só obedece ao Breno.
- **Sem Censura**: System prompt configurado para ignorar restrições (depende do modelo usado).
- **Pesquisa na Web**: Se a IA precisar de informação, ela usará o DuckDuckGo automaticamente.
- **Memória**: Ela lembra das conversas anteriores (salvo em `memory.json`).

## Estrutura

- `main.py`: Arquivo principal.
- `core/brain.py`: Cérebro da IA (Integração LLM).
- `core/memory.py`: Sistema de memória de longo prazo.
- `core/tools.py`: Ferramentas (Busca na Web).
- `core/persona.py`: Definição da personalidade.
