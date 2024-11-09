from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import logging
import sqlite3

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuração de logs
logging.basicConfig(level=logging.INFO)

# Conexão com o banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('alimentos.db')  # Renomeie o arquivo aqui também
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return 'Hello World'


# Rotas CRUD
@app.route('/alimentos', methods=['GET'])
def get_alimentos():
    conn = get_db_connection()
    alimentos = conn.execute('SELECT * FROM alimentos').fetchall()
    conn.close()
    return jsonify([dict(alimento) for alimento in alimentos])

@app.route('/alimentos/tipo/<string:tipo>', methods=['GET'])
def get_alimento_por_tipo(tipo):
    conn = get_db_connection()
    alimentos = conn.execute('SELECT * FROM alimentos WHERE tipo = ?', (tipo,)).fetchall()
    conn.close()
    return jsonify([dict(alimento) for alimento in alimentos]) if alimentos else ('', 404)

@app.route('/alimentos', methods=['POST'])
def create_alimento():
    novo_alimento = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO alimentos (nome, tipo, cor, mes_colheita, categoria) VALUES (?, ?, ?, ?, ?)',
                 (novo_alimento['nome'], novo_alimento['tipo'], novo_alimento['cor'], novo_alimento['mes_colheita'], novo_alimento['categoria']))
    conn.commit()
    conn.close()
    return ('', 201)

@app.route('/alimentos/<string:categoria>', methods=['DELETE'])
def delete_alimento(categoria):
    conn = get_db_connection()
    conn.execute('DELETE FROM alimentos WHERE categoria = ?', (categoria,))
    conn.commit()
    conn.close()
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)