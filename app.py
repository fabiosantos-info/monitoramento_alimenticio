import os
import logging
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import sqlite3

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Criação do diretório de logs se não existir
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)

# Configuração de logs
log_file_path = os.path.join(log_directory, 'flask_app.log')  # Caminho completo do arquivo de log
logging.basicConfig(
    filename=log_file_path,  # Nome do arquivo de log na pasta logs
    level=logging.INFO,  # Nível de log (INFO, DEBUG, ERROR, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato da mensagem de log
)

# Conexão com o banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('alimentos.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    app.logger.info('Acessada a rota /')
    return 'Hello World'

# Rotas CRUD
@app.route('/alimentos', methods=['GET'])
def get_alimentos():
    app.logger.info('Acessada a rota /alimentos com método GET')
    conn = get_db_connection()
    alimentos = conn.execute('SELECT * FROM alimentos').fetchall()
    conn.close()
    return jsonify([dict(alimento) for alimento in alimentos])

@app.route('/alimentos/tipo/<string:tipo>', methods=['GET'])
def get_alimento_por_tipo(tipo):
    app.logger.info(f'Acessada a rota /alimentos/tipo/{tipo} com método GET')
    conn = get_db_connection()
    alimentos = conn.execute('SELECT * FROM alimentos WHERE tipo = ?', (tipo,)).fetchall()
    conn.close()
    
    if alimentos:
        return jsonify([dict(alimento) for alimento in alimentos])
    else:
        return jsonify({"message": f"Nenhum alimento encontrado para o tipo '{tipo}'."}), 404

@app.route('/alimentos', methods=['POST'])
def create_alimento():
    novo_alimento = request.json
    app.logger.info(f'Inserindo novo alimento: {novo_alimento}')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO alimentos (nome, tipo, cor, mes_colheita, categoria) VALUES (?, ?, ?, ?, ?)',
                 (novo_alimento['nome'], novo_alimento['tipo'], novo_alimento['cor'], novo_alimento['mes_colheita'], novo_alimento['categoria']))
    
    conn.commit()
    conn.close()
    
    return ('', 201)

@app.route('/alimentos/<string:categoria>', methods=['DELETE'])
def delete_alimento(categoria):
    app.logger.info(f'Removendo alimentos da categoria: {categoria}')
    
    conn = get_db_connection()
    conn.execute('DELETE FROM alimentos WHERE categoria = ?', (categoria,))
    
    conn.commit()
    conn.close()
    
    return ('', 204)

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Desculpe, a rota que você tentou acessar não foi encontrada."}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Ocorreu um erro interno no servidor. Tente novamente mais tarde."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)