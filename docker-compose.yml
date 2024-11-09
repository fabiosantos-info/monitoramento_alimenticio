import os
import json
import logging
import sqlite3
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Inicialização do Flask
app = Flask(__name__)
CORS(app)

# Configuração do logging
handler = logging.FileHandler('logs/flask_app.log')
app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Métricas Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total de requisições HTTP', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'Latência das requisições HTTP em segundos', ['method', 'endpoint'])
HTTP_ERRORS = Counter('http_errors_total', 'Total de respostas HTTP com erro', ['method', 'endpoint', 'status_code'])

# Middleware para contar requisições
@app.before_request
def before_request():
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()

# Rota para o Prometheus coletar as métricas
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Função para logar mensagens
def log_message(level, message):
    log_methods = {
        'debug': app.logger.debug,
        'info': app.logger.info,
        'warning': app.logger.warning,
        'error': app.logger.error,
        'critical': app.logger.critical
    }
    log_methods.get(level, app.logger.error)(message)

@app.route('/')
def home():
    return "API de pessoas"

# Endpoint para listar todas as pessoas
@app.route('/pessoas', methods=['GET'])
def pessoas():
    try:
        with sqlite3.connect('crud.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT nome, sobrenome, cpf, data_nascimento FROM pessoa')
            result = cursor.fetchall()
            app.logger.info(f"GET /pessoas - Total de pessoas retornadas: {len(result)}")
            return jsonify([dict(ix) for ix in result]), 200
    except Exception as e:
        app.logger.error(f"Erro ao buscar pessoas: {str(e)}")
        return jsonify(error=str(e)), 500

# Endpoint para obter ou deletar uma pessoa por CPF
@app.route('/pessoa/<cpf>', methods=['GET', 'DELETE'])
def pessoa_por_cpf(cpf):
    try:
        with sqlite3.connect('crud.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if request.method == 'GET':
                cursor.execute('SELECT nome, sobrenome, cpf, data_nascimento FROM pessoa WHERE cpf=?', [cpf])
                result = cursor.fetchall()
                if result:
                    app.logger.info(f"GET /pessoa/{cpf} - Pessoa encontrada.")
                    return jsonify([dict(ix) for ix in result]), 200
                app.logger.warning(f"GET /pessoa/{cpf} - Pessoa não encontrada.")
                return jsonify(error="Pessoa não encontrada"), 404
            
            elif request.method == 'DELETE':
                cursor.execute('DELETE FROM pessoa WHERE cpf = ?', (cpf,))
                if cursor.rowcount == 0:
                    app.logger.warning(f"DELETE /pessoa/{cpf} - Pessoa não encontrada.")
                    return jsonify(error="Pessoa não encontrada"), 404
                conn.commit()
                app.logger.info(f"DELETE /pessoa/{cpf} - Pessoa deletada com sucesso.")
                return jsonify(success="Pessoa deletada com sucesso"), 200
    except Exception as e:
        app.logger.error(f"Erro ao processar a requisição para /pessoa/{cpf}: {str(e)}")
        return jsonify(error=str(e)), 500

# Endpoint para inserir ou atualizar uma pessoa
@app.route('/pessoa', methods=['POST'])
def insere_atualiza_pessoa():
    data = request.get_json(force=True)
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    cpf = data.get('cpf')
    datanascimento = data.get('data_nascimento')
    try:
        with sqlite3.connect('crud.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM pessoa WHERE cpf = ?', (cpf,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute('UPDATE pessoa SET nome=?, sobrenome=?, data_nascimento=? WHERE cpf=?', 
                               (nome, sobrenome, datanascimento, cpf))
                conn.commit()
                app.logger.info(f"POST /pessoa - Pessoa com CPF {cpf} atualizada.")
                return jsonify(success="Pessoa atualizada com sucesso"), 200
            
            cursor.execute('INSERT INTO pessoa (nome, sobrenome, cpf, data_nascimento) VALUES (?, ?, ?, ?)', 
                           (nome, sobrenome, cpf, datanascimento))
            conn.commit()
            app.logger.info(f"POST /pessoa - Nova pessoa inserida: {nome} {sobrenome}.")
            return jsonify(success="Pessoa inserida com sucesso"), 201
    except Exception as e:
        app.logger.error(f"Erro ao inserir/atualizar pessoa: {str(e)}")
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
