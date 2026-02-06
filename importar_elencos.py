#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARSER FINAL COMPLETO - Detecta TODOS os formatos do RTF
"""

import re
import sqlite3
import os

def decodificar_rtf_char(match):
    codigo = match.group(1)
    try:
        return bytes.fromhex(codigo).decode('latin1')
    except:
        return '?'

def limpar_texto_rtf(texto):
    texto = re.sub(r"\\'([0-9a-fA-F]{2})", decodificar_rtf_char, texto)
    texto = re.sub(r'\\[a-z]+\d*\s?', '', texto)
    texto = re.sub(r'[{}]', '', texto)
    return texto.strip()

def extrair_elencos_completo(arquivo_rtf):
    """
    Extrai elencos detectando TRÊS formatos diferentes:
    
    FORMATO 1 (maioria): \\b TITULO\\par ... de/direção ... \\par\\par ELENCO
    FORMATO 2 (raros): \\b TITULO\\par\\par\\b0 ELENCO  
    FORMATO 3 (sem créditos): \\b TITULO\\par\\b0 ELENCO
    """
    
    with open(arquivo_rtf, 'r', encoding='latin1', errors='ignore') as f:
        conteudo = f.read()
    
    producoes = []
    erros = []
    
    blocos = re.split(r'\\b\s+', conteudo)
    
    palavras_credito = {
        'de', 'direção', 'direcao', 'colaboração', 'colaboracao',
        'diretor', 'diretores', 'autor', 'autores',
        'roteiro', 'roteirista', 'roteiristas',
        'adaptação', 'adaptacao', 'baseado',
        'supervisão', 'supervisao', 'produtor', 'produtores',
        'producao', 'produção', 'cenografia', 'figurino',
        'trilha', 'sonora', 'abertura', 'núcleo', 'nucleo',
        'coordenação', 'coordenacao', 'assistente', 'assistentes',
        'e'  # palavra "e" sozinha entre créditos
    }
    
    for i, bloco in enumerate(blocos):
        if i == 0:
            continue
        
        bloco = bloco.replace('\\b0', '')
        
        # Captura título: qualquer coisa exceto quebra de linha até \par
        # Isso permite códigos RTF como \'e3 (ã), \'e7 (ç), etc
        match_titulo = re.match(r'^([^\r\n]+?)\\par', bloco)
        if not match_titulo:
            continue
        
        titulo_raw = match_titulo.group(1)
        titulo = limpar_texto_rtf(titulo_raw)
        
        if not titulo or len(titulo) < 2:
            continue
        
        resto = bloco[match_titulo.end():]
        
        # DETECTA FORMATO
        # Formato 2/3: Tem \\b0 logo após o título (sem créditos ou créditos mínimos)
        if resto.strip().startswith('\\b0') or '\\par\\par' in resto[:50]:
            # Formato simplificado - pega tudo após primeira linha vazia
            linhas = re.split(r'\\par', resto)
            elenco = []
            
            for linha in linhas:
                linha_limpa = limpar_texto_rtf(linha)
                
                if not linha_limpa or len(linha_limpa) < 3:
                    continue
                
                # Pula palavras de crédito
                if linha_limpa.lower() in palavras_credito:
                    continue
                
                # Para em marcadores de fase
                if linha_limpa.lower() in ['1ª fase', '2ª fase', '3ª fase']:
                    break
                
                elenco.append({'ator': linha_limpa, 'personagem': None})
        
        else:
            # Formato 1: Tem créditos (de/direção) seguidos de linha vazia dupla
            linhas = re.split(r'\\par', resto)
            elenco = []
            modo = 'creditos'
            linhas_vazias = 0
            
            for linha in linhas:
                linha_limpa = limpar_texto_rtf(linha)
                
                if not linha_limpa or len(linha_limpa) < 2:
                    linhas_vazias += 1
                    if linhas_vazias >= 1 and modo == 'creditos':
                        modo = 'elenco'
                    continue
                
                linhas_vazias = 0
                linha_lower = linha_limpa.lower()
                
                if modo == 'creditos':
                    if linha_lower in palavras_credito:
                        continue
                    continue
                
                if modo == 'elenco':
                    if linha_lower in ['1ª fase', '2ª fase', '3ª fase']:
                        break
                    
                    elenco.append({'ator': linha_limpa, 'personagem': None})
        
        # Valida elenco  
        # Mínimo 2 atores (algumas produções pequenas têm mesmo poucos)
        if len(elenco) >= 2:
            producoes.append({
                'titulo': titulo,
                'tipo': 'Novela',
                'ano_inicio': None,
                'ano_fim': None,
                'elenco': elenco
            })
            print(f"✓ {titulo}: {len(elenco)} atores")
        elif len(elenco) > 0:
            erros.append(f"⚠️  {titulo}: apenas {len(elenco)} ator(es)")
    
    if erros:
        print("\n" + "="*70)
        print("AVISOS (produções muito pequenas):")
        for erro in erros:
            print(erro)
    
    return producoes

def criar_banco_limpo(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE producoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            ano_inicio INTEGER,
            ano_fim INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE atores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE elenco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ator_id INTEGER NOT NULL,
            producao_id INTEGER NOT NULL,
            personagem TEXT,
            FOREIGN KEY (ator_id) REFERENCES atores (id),
            FOREIGN KEY (producao_id) REFERENCES producoes (id),
            UNIQUE(ator_id, producao_id)
        )
    ''')
    
    cursor.execute('CREATE INDEX idx_atores_nome ON atores(nome)')
    cursor.execute('CREATE INDEX idx_elenco_ator ON elenco(ator_id)')
    cursor.execute('CREATE INDEX idx_elenco_producao ON elenco(producao_id)')
    
    conn.commit()
    conn.close()

def importar_para_banco(producoes, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    total_producoes = 0
    total_participacoes = 0
    
    for producao in producoes:
        try:
            cursor.execute('''
                INSERT INTO producoes (titulo, tipo, ano_inicio, ano_fim)
                VALUES (?, ?, ?, ?)
            ''', (producao['titulo'], producao['tipo'],
                  producao.get('ano_inicio'), producao.get('ano_fim')))
            
            producao_id = cursor.lastrowid
            total_producoes += 1
            
            for participacao in producao['elenco']:
                ator_nome = participacao['ator']
                
                cursor.execute('INSERT OR IGNORE INTO atores (nome) VALUES (?)', (ator_nome,))
                cursor.execute('SELECT id FROM atores WHERE nome = ?', (ator_nome,))
                result = cursor.fetchone()
                
                if result:
                    ator_id = result[0]
                    try:
                        cursor.execute('''
                            INSERT INTO elenco (ator_id, producao_id, personagem)
                            VALUES (?, ?, ?)
                        ''', (ator_id, producao_id, participacao.get('personagem')))
                        total_participacoes += 1
                    except sqlite3.IntegrityError:
                        pass
        
        except Exception as e:
            print(f"❌ Erro ao importar '{producao['titulo']}': {e}")
    
    conn.commit()
    conn.close()
    
    return total_producoes, total_participacoes

def verificar_dados(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("VERIFICAÇÃO FINAL")
    print("="*70)
    
    cursor.execute('SELECT COUNT(*) FROM producoes')
    total_producoes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM atores')
    total_atores = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM elenco')
    total_participacoes = cursor.fetchone()[0]
    
    print(f"\n📊 Estatísticas:")
    print(f"   • {total_producoes} produções")
    print(f"   • {total_atores} atores únicos")
    print(f"   • {total_participacoes} participações")
    
    # Testa casos específicos
    print(f"\n🎯 Testes:")
    
    cursor.execute('''
        SELECT COUNT(*) FROM producoes p
        JOIN elenco e ON p.id = e.producao_id
        JOIN atores a ON e.ator_id = a.id
        WHERE p.titulo = 'Roque Santeiro' AND a.nome = 'LIMA DUARTE'
    ''')
    print(f"   {'✅' if cursor.fetchone()[0] > 0 else '❌'} Lima Duarte em Roque Santeiro")
    
    cursor.execute('''
        SELECT COUNT(*) FROM producoes WHERE titulo = 'Cidade dos Homens'
    ''')
    print(f"   {'✅' if cursor.fetchone()[0] > 0 else '❌'} Cidade dos Homens importada")
    
    cursor.execute('''
        SELECT COUNT(DISTINCT p.id) FROM producoes p
        JOIN elenco e ON p.id = e.producao_id
        JOIN atores a ON e.ator_id = a.id
        WHERE a.nome LIKE '%FERNANDA MONTENEGRO%'
    ''')
    count = cursor.fetchone()[0]
    print(f"   📺 Fernanda Montenegro: {count} produções")
    
    conn.close()

if __name__ == '__main__':
    print("="*70)
    print("PARSER FINAL COMPLETO - TODOS OS FORMATOS")
    print("="*70)
    
    db_path = 'novelas_globo.db'
    
    print("\n1️⃣ Criando banco limpo...")
    criar_banco_limpo(db_path)
    
    print("\n2️⃣ Extraindo elencos (TODOS os formatos)...")
    producoes = extrair_elencos_completo('/mnt/user-data/uploads/elencos.rtf')
    
    print(f"\n3️⃣ Importando {len(producoes)} produções...")
    total_prod, total_part = importar_para_banco(producoes, db_path)
    
    print(f"\n✅ {total_prod} produções • {total_part} participações")
    
    verificar_dados(db_path)
    
    print("\n" + "="*70)
    print(f"✅ BANCO COMPLETO: {db_path}")
    print("="*70)
