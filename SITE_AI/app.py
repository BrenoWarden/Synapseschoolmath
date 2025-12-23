import sys
import os
import threading
import time
from flask import Flask, render_template, request, redirect, session, jsonify, Response, stream_with_context

# Configuração de caminhos
# Resolve o caminho da IA para ambientes locais (Windows) e produção (Railway)
AI_PATH_ENV = os.environ.get("AI_PATH", "")
if AI_PATH_ENV and os.path.isdir(AI_PATH_ENV):
    AI_PATH = AI_PATH_ENV
else:
    # Tenta caminho relativo dentro do repositório
    repo_ai_path = os.path.join(os.path.dirname(__file__), "IA_BRENO")
    if os.path.isdir(repo_ai_path):
        AI_PATH = repo_ai_path
    elif os.path.isdir(r"C:\Users\AMD\Desktop\IA\IA_BRENO"):
        AI_PATH = r"C:\Users\AMD\Desktop\IA\IA_BRENO"
    else:
        print("Não foi possível localizar a pasta IA_BRENO. Defina AI_PATH como variável de ambiente ou inclua IA_BRENO no repositório.")
        sys.exit(1)
sys.path.append(AI_PATH)

# Importando módulos da IA
try:
    from core.brain import Brain
    from core.memory import Memory
    from core.persona import get_system_prompt
    from config import USER_NAME, AI_NAME, MEMORY_FILE
except ImportError as e:
    print(f"Erro ao importar módulos da IA: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_e_segura' # Em produção, use uma env var
@app.before_request
def require_login():
    allowed_paths = {'/login', '/logout'}
    if request.path.startswith('/static') or request.path == '/favicon.ico':
        return
    if not session.get('logged_in') and request.path not in allowed_paths:
        return redirect('/login')

# Credenciais
VALID_USER = "Breno"
VALID_PASS = "BRgg@7131912"

# --- CLASSE WRAPPER PARA GARANTIR FUNCIONAMENTO SEM CENSURA ---
class WebBrain(Brain):
    """
    Uma versão especializada do cérebro da IA para a Web.
    Garante que as diretrizes de personalidade (sem censura) sejam recarregadas
    a cada interação, ignorando estados anteriores que possam ter causado bloqueios.
    """
    def think(self, user_input):
        # Recarrega o prompt do sistema diretamente do arquivo persona.py
        self.system_prompt = get_system_prompt()
        return super().think(user_input)

    def think_stream(self, user_input):
        # Recarrega o prompt do sistema para o stream também
        self.system_prompt = get_system_prompt()
        # Retorna o gerador do método original
        return super().think_stream(user_input)

# Inicialização da IA
print("Inicializando IA...")

# Importante: O caminho do arquivo de memória deve ser absoluto ou relativo à pasta da IA
if os.path.isabs(MEMORY_FILE):
    memory_path = MEMORY_FILE
else:
    memory_path = os.path.join(AI_PATH, MEMORY_FILE)

print(f"Carregando memória de: {memory_path}")
memory = Memory(file_path=memory_path)

# Usando o WebBrain em vez do Brain padrão
brain = WebBrain(memory)
print("IA Pronta e totalmente carregada (Modo Web Sem Censura).")

def shutdown_server():
    """Função para encerrar o servidor"""
    print("Encerrando o servidor por tentativa de acesso não autorizado...")
    os._exit(0)

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect('/chat')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == VALID_USER and password == VALID_PASS:
            session['logged_in'] = True
            session['user'] = username
            return redirect('/chat')
        else:
            error_msg = "ACESSO NEGADO. Credenciais inválidas. O sistema será encerrado."
            threading.Timer(3.0, shutdown_server).start()
            return render_template('login.html', error=error_msg)
    
    return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('chat.html')

@app.route('/api/message', methods=['POST'])
def api_message():
    # Mantendo compatibilidade com código antigo, mas o frontend deve usar /api/stream agora
    if not session.get('logged_in'):
        return jsonify({'error': 'Não autorizado'}), 403
    
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'Mensagem vazia'}), 400

    try:
        response = brain.think(user_input)
        memory.add_interaction(user_input, response)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Erro na IA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream', methods=['POST'])
def api_stream():
    if not session.get('logged_in'):
        return jsonify({'error': 'Não autorizado'}), 403
    
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'Mensagem vazia'}), 400

    def generate():
        full_response = ""
        try:
            for chunk in brain.think_stream(user_input):
                if chunk:
                    full_response += chunk
                    yield chunk
            
            # Salva na memória após conclusão do stream
            memory.add_interaction(user_input, full_response)
        except Exception as e:
            yield f"\n[ERRO NO STREAM]: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route('/api/undo', methods=['POST'])
def api_undo():
    """Remove a última interação da memória (para regeneração)"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Não autorizado'}), 403
    
    try:
        memory.remove_last_interaction()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    if not session.get('logged_in'):
        return jsonify({'error': 'Não autorizado'}), 403
    data = request.json
    msg = data.get('message', '')
    kind = data.get('type', '')
    try:
        memory.add_feedback(msg, kind)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = not os.environ.get('PORT')  # Se PORT existir (Railway), desliga debug
    if debug:
        extra_files = [
            os.path.join(AI_PATH, 'core', 'brain.py'),
            os.path.join(AI_PATH, 'core', 'persona.py'),
            os.path.join(AI_PATH, 'core', 'tools.py'),
            os.path.join(AI_PATH, 'core', 'memory.py'),
            os.path.join(AI_PATH, 'config.py')
        ]
        app.run(host=host, port=port, debug=True, extra_files=extra_files)
    else:
        app.run(host=host, port=port, debug=False)
