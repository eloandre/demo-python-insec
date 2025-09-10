"""
insecure-python-app/app.py

Aplicação Flask intencionalmente insegura - fins educativos.

Vulnerabilidades incluídas:
- Credenciais e API key hardcoded
- SQL Injection (execução de query construída por concatenação)
- Cross-Site Scripting (XSS) reflexivo via template sem escape
- Remote Code Execution (simulada/desativada)
- Uso de dependências antigas (ver requirements.txt)
"""

from flask import Flask, request, jsonify, render_template_string, g
import sqlite3
import os
import html

app = Flask(__name__)

# ---------- Credenciais / API key hardcoded (INSEGURAS) ----------
USER = "admin_user"
PASS = "P@ssw0rd-fiCticio"
API_KEY = "sk_test_FAKE_PY_1234567890"

# ---------- Banco SQLite simples (arquivo) ----------
DATABASE = 'insecure.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

def init_db():
    # Cria tabela e popula alguns usuários (apenas local)
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)')
    cur.execute("DELETE FROM users")  # reset para fins educacionais
    cur.executemany("INSERT INTO users (username, email) VALUES (?, ?)", [
        ('alice', 'alice@example.com'),
        ('bob', 'bob@example.com'),
        ('charlie', 'charlie@example.com'),
    ])
    conn.commit()
    conn.close()

# Inicializa DB ao iniciar (apenas para demo)
init_db()

# ---------- Rotas vulneráveis ----------

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    # Vulnerabilidade: autenticação com credenciais hardcoded
    if username == USER and password == PASS:
        return jsonify({"ok": True, "msg": "Autenticado (fictício)."}), 200

    return jsonify({"ok": False, "msg": "Credenciais inválidas."}), 401

@app.route('/search-users', methods=['GET'])
def search_users():
    """
    Exemplo de SQL injection: constrói a query concatenando a entrada do usuário.
    Em um banco real isso permitiria injeção. Aqui usamos sqlite para demonstrar.
    """
    q = request.args.get('q', '')

    # Vulnerável: concatenação direta em SQL
    vulnerable_sql = f"SELECT * FROM users WHERE username LIKE '%{q}%' OR email LIKE '%{q}%'"
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(vulnerable_sql)  # execução insegura INTENCIONAL
        rows = cur.fetchall()
        results = [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]
    except Exception as e:
        results = []
        # retornamos a query pra estudo/inspeção
    return jsonify({
        "note": "Esta rota demonstra SQL construído por concatenação (vulnerável).",
        "vulnerable_sql": vulnerable_sql,
        "results": results
    })

@app.route('/greet', methods=['GET'])
def greet():
    """
    XSS reflexivo: injeta a entrada do usuário diretamente no template sem escape.
    Use ?name=<script>alert(1)</script> para ver vulnerabilidade (em ambiente isolado).
    """
    name = request.args.get('name', 'visitante')

    # Vulnerável: insere input no template sem escape
    unsafe_template = """
    <html>
      <body>
        <h1>Olá, {{ name }}!</h1>
        <p>Esta página é vulnerável a XSS reflexivo.</p>
        <hr/>
        <p>Raw name: {{ raw }}</p>
      </body>
    </html>
    """
    # NOTE: render_template_string usará Jinja2 (a versão do requirements é antiga)
    return render_template_string(unsafe_template, name=name, raw=name)

@app.route('/greet-safe', methods=['GET'])
def greet_safe():
    """
    Versão 'segura' para comparação: escapa o input antes de renderizar.
    """
    name = request.args.get('name', 'visitante')
    safe_name = html.escape(name)
    safe_template = f"<h1>Olá, {safe_name}!</h1><p>Versão segura (escape aplicado).</p>"
    return safe_template

@app.route('/run-command', methods=['POST'])
def run_command():
    """
    RCE demonstrada como SIMULAÇÃO: NÃO execute input do usuário.
    Aqui mostramos o comando que seria executado, sem executá-lo.
    """
    data = request.json or {}
    cmd = data.get('cmd', '')

    # Exemplo perigoso (DESATIVADO)
    import subprocess
    subprocess.call(cmd, shell=True)  # NÃO FAÇA ISSO

    return jsonify({
        "note": "RCE demonstrada apenas como simulação. O comando NÃO foi executado.",
        "would_run": cmd
    })

@app.route('/pay', methods=['GET'])
def pay():
    """
    Exposição de API key embutida no código (exemplo inseguro).
    """
    return jsonify({
        "note": "Endpoint de pagamento (simulado). Chave embutida no código (inseguro).",
        "api_key": API_KEY
    })

# ---------- Rota para explicar como mitigar (educacional) ----------
@app.route('/mitigations', methods=['GET'])
def mitigations():
    advices = [
        "Não armazene credenciais ou chaves no código-fonte — use segredos/variáveis de ambiente.",
        "Use consultas parametrizadas (prepared statements) — não concatene strings SQL com input do usuário.",
        "Escape ou sanitize input antes de renderizar em páginas HTML; use templates atualizados.",
        "Nunca execute comandos do usuário no shell; se necessário, valide estritamente e use listas brancas.",
        "Mantenha dependências atualizadas e monitore por pacotes comprometidos."
    ]
    return jsonify({"advice": advices})

if __name__ == "__main__":
    # Executa em 0.0.0.0 para facilitar testes dentro de container; porta 3000 para manter consistência
    app.run(host='0.0.0.0', port=3000, debug=True)

