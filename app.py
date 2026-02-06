#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask para o sistema de busca de novelas/minisséries da Globo
"""

from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    """Cria conexão com o banco de dados"""
    conn = sqlite3.connect('novelas_globo.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve a página principal"""
    return send_from_directory('.', 'index.html')

@app.route('/api/buscar', methods=['GET'])
def buscar_ator():
    """
    Busca produções por nome do ator
    Parâmetros: nome (query string)
    """
    nome = request.args.get('nome', '').strip()
    
    if not nome or len(nome) < 2:
        return jsonify({
            'erro': 'Digite pelo menos 2 caracteres para buscar'
        }), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca com LIKE para permitir busca parcial
    query = '''
        SELECT 
            a.nome as ator,
            p.titulo,
            p.tipo,
            p.ano_inicio,
            p.ano_fim,
            e.personagem
        FROM atores a
        JOIN elenco e ON a.id = e.ator_id
        JOIN producoes p ON e.producao_id = p.id
        WHERE a.nome LIKE ?
        ORDER BY p.ano_inicio DESC, p.titulo
    '''
    
    cursor.execute(query, (f'%{nome}%',))
    resultados = cursor.fetchall()
    conn.close()
    
    if not resultados:
        return jsonify({
            'ator': nome,
            'total': 0,
            'producoes': []
        })
    
    # Organiza os resultados
    ator_nome = resultados[0]['ator']
    producoes = []
    
    for row in resultados:
        anos = f"{row['ano_inicio']}"
        if row['ano_fim'] and row['ano_fim'] != row['ano_inicio']:
            anos += f"-{row['ano_fim']}"
        
        producoes.append({
            'titulo': row['titulo'],
            'tipo': row['tipo'],
            'anos': anos,
            'personagem': row['personagem'] or 'Não especificado'
        })
    
    return jsonify({
        'ator': ator_nome,
        'total': len(producoes),
        'producoes': producoes
    })

@app.route('/api/atores', methods=['GET'])
def listar_atores():
    """Lista todos os atores para autocomplete"""
    termo = request.args.get('termo', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if termo and len(termo) >= 2:
        cursor.execute('''
            SELECT nome FROM atores 
            WHERE nome LIKE ?
            ORDER BY nome
            LIMIT 20
        ''', (f'%{termo}%',))
    else:
        cursor.execute('SELECT nome FROM atores ORDER BY nome LIMIT 20')
    
    atores = [row['nome'] for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(atores)

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas gerais do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM atores')
    total_atores = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM producoes')
    total_producoes = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'total_atores': total_atores,
        'total_producoes': total_producoes
    })

if __name__ == '__main__':
    # Verifica se o banco existe
    if not os.path.exists('novelas_globo.db'):
        print("ERRO: Banco de dados não encontrado!")
        print("Execute primeiro: python criar_banco.py")
        exit(1)
    
    print("="*60)
    print("SERVIDOR INICIADO!")
    print("="*60)
    print("Acesse: http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
