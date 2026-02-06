#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar e popular o banco de dados de novelas/minisséries da Globo
"""

import sqlite3
import json

def criar_banco():
    """Cria as tabelas do banco de dados"""
    conn = sqlite3.connect('novelas_globo.db')
    cursor = conn.cursor()
    
    # Tabela de produções (novelas/minisséries)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS producoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            ano_inicio INTEGER,
            ano_fim INTEGER
        )
    ''')
    
    # Tabela de atores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela de relacionamento (elenco)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elenco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ator_id INTEGER NOT NULL,
            producao_id INTEGER NOT NULL,
            personagem TEXT,
            FOREIGN KEY (ator_id) REFERENCES atores (id),
            FOREIGN KEY (producao_id) REFERENCES producoes (id)
        )
    ''')
    
    # Índices para melhorar performance de busca
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_atores_nome ON atores(nome)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_elenco_ator ON elenco(ator_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_elenco_producao ON elenco(producao_id)')
    
    conn.commit()
    conn.close()
    print("✓ Banco de dados criado com sucesso!")

def importar_dados_exemplo():
    """Importa dados de exemplo para testar o sistema"""
    conn = sqlite3.connect('novelas_globo.db')
    cursor = conn.cursor()
    
    # Dados de exemplo
    dados_exemplo = [
        {
            "titulo": "Vale Tudo",
            "tipo": "Novela",
            "ano_inicio": 1988,
            "ano_fim": 1989,
            "elenco": [
                {"ator": "Regina Duarte", "personagem": "Raquel Accioli"},
                {"ator": "Beatriz Segall", "personagem": "Odete Roitman"},
                {"ator": "Antônio Fagundes", "personagem": "Ivan Meirelles"},
                {"ator": "Glória Pires", "personagem": "Maria de Fátima"}
            ]
        },
        {
            "titulo": "Roque Santeiro",
            "tipo": "Novela",
            "ano_inicio": 1985,
            "ano_fim": 1986,
            "elenco": [
                {"ator": "Regina Duarte", "personagem": "Viúva Porcina"},
                {"ator": "Lima Duarte", "personagem": "Sinhôzinho Malta"},
                {"ator": "José Wilker", "personagem": "Roque Santeiro"}
            ]
        },
        {
            "titulo": "Avenida Brasil",
            "tipo": "Novela",
            "ano_inicio": 2012,
            "ano_fim": 2012,
            "elenco": [
                {"ator": "Adriana Esteves", "personagem": "Carminha"},
                {"ator": "Cauã Reymond", "personagem": "Tufão"},
                {"ator": "Débora Falabella", "personagem": "Nina/Rita"}
            ]
        },
        {
            "titulo": "Pantanal",
            "tipo": "Novela",
            "ano_inicio": 2022,
            "ano_fim": 2022,
            "elenco": [
                {"ator": "Marcos Palmeira", "personagem": "José Leôncio"},
                {"ator": "Dira Paes", "personagem": "Fiô"},
                {"ator": "Murilo Benício", "personagem": "Tenório"}
            ]
        },
        {
            "titulo": "A Grande Família",
            "tipo": "Série",
            "ano_inicio": 2001,
            "ano_fim": 2014,
            "elenco": [
                {"ator": "Marco Nanini", "personagem": "Lineu Silva"},
                {"ator": "Marieta Severo", "personagem": "Nenê Silva"},
                {"ator": "Marcos Oliveira", "personagem": "Beiçola"}
            ]
        }
    ]
    
    for producao in dados_exemplo:
        # Insere a produção
        cursor.execute('''
            INSERT INTO producoes (titulo, tipo, ano_inicio, ano_fim)
            VALUES (?, ?, ?, ?)
        ''', (producao['titulo'], producao['tipo'], producao['ano_inicio'], producao['ano_fim']))
        
        producao_id = cursor.lastrowid
        
        # Insere os atores e relacionamentos
        for participacao in producao['elenco']:
            # Tenta inserir o ator (ou ignora se já existe)
            cursor.execute('''
                INSERT OR IGNORE INTO atores (nome) VALUES (?)
            ''', (participacao['ator'],))
            
            # Busca o ID do ator
            cursor.execute('SELECT id FROM atores WHERE nome = ?', (participacao['ator'],))
            ator_id = cursor.fetchone()[0]
            
            # Insere o relacionamento no elenco
            cursor.execute('''
                INSERT INTO elenco (ator_id, producao_id, personagem)
                VALUES (?, ?, ?)
            ''', (ator_id, producao_id, participacao.get('personagem')))
    
    conn.commit()
    conn.close()
    print("✓ Dados de exemplo importados com sucesso!")

def importar_de_json(arquivo_json):
    """
    Importa dados de um arquivo JSON
    
    Formato esperado do JSON:
    [
        {
            "titulo": "Nome da Novela",
            "tipo": "Novela",
            "ano_inicio": 2020,
            "ano_fim": 2021,
            "elenco": [
                {"ator": "Nome do Ator", "personagem": "Nome do Personagem"},
                ...
            ]
        },
        ...
    ]
    """
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        conn = sqlite3.connect('novelas_globo.db')
        cursor = conn.cursor()
        
        for producao in dados:
            # Insere a produção
            cursor.execute('''
                INSERT INTO producoes (titulo, tipo, ano_inicio, ano_fim)
                VALUES (?, ?, ?, ?)
            ''', (producao['titulo'], producao['tipo'], 
                  producao.get('ano_inicio'), producao.get('ano_fim')))
            
            producao_id = cursor.lastrowid
            
            # Insere os atores e relacionamentos
            for participacao in producao.get('elenco', []):
                cursor.execute('''
                    INSERT OR IGNORE INTO atores (nome) VALUES (?)
                ''', (participacao['ator'],))
                
                cursor.execute('SELECT id FROM atores WHERE nome = ?', (participacao['ator'],))
                ator_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    INSERT INTO elenco (ator_id, producao_id, personagem)
                    VALUES (?, ?, ?)
                ''', (ator_id, producao_id, participacao.get('personagem')))
        
        conn.commit()
        conn.close()
        print(f"✓ Dados importados de {arquivo_json} com sucesso!")
        
    except FileNotFoundError:
        print(f"✗ Arquivo {arquivo_json} não encontrado!")
    except json.JSONDecodeError:
        print(f"✗ Erro ao ler JSON do arquivo {arquivo_json}")
    except Exception as e:
        print(f"✗ Erro ao importar dados: {e}")

if __name__ == '__main__':
    print("Criando banco de dados...")
    criar_banco()
    
    print("\nImportando dados de exemplo...")
    importar_dados_exemplo()
    
    print("\n" + "="*50)
    print("BANCO DE DADOS PRONTO!")
    print("="*50)
    print("\nPara importar seus dados:")
    print("1. Crie um arquivo JSON no formato especificado")
    print("2. Execute: python criar_banco.py seu_arquivo.json")
    print("\nOu use o código:")
    print("  from criar_banco import importar_de_json")
    print("  importar_de_json('seu_arquivo.json')")
