# 📺 IMPORTANDO SEUS ELENCOS DA GLOBO

## ✅ PROCESSO COMPLETO - PASSO A PASSO

### 1️⃣ Instale o Flask
```bash
pip install flask
```

### 2️⃣ Crie o banco de dados vazio
```bash
python criar_banco.py
```

### 3️⃣ Importe o arquivo de elencos
```bash
python importar_elencos.py
```

**Resultado esperado:**
```
============================================================
PROCESSANDO ARQUIVO RTF DE ELENCOS
============================================================

1. Lendo arquivo: /mnt/user-data/uploads/elencos.rtf
   ✓ 337 produções encontradas

2. Importando para o banco de dados...
   ✓ 337 produções importadas
   ✓ 15387 participações registradas

============================================================
IMPORTAÇÃO CONCLUÍDA!
============================================================
Total no banco:
  • 4669 atores únicos
  • 337 produções
============================================================
```

### 4️⃣ Inicie o servidor
```bash
python app.py
```

### 5️⃣ Acesse no navegador
```
http://localhost:5000
```

---

## 🎯 O QUE FOI IMPORTADO

✅ **337 novelas e minisséries** da Globo  
✅ **4.669 atores únicos**  
✅ **15.387 participações** (ator + produção)  

Exemplos de produções importadas:
- Bicho do Mato
- A Patota
- Helena
- Senhora
- A Moreninha
- Escrava Isaura
- Vale Tudo
- Roque Santeiro
- E muitas outras!

---

## 🔍 TESTANDO O SISTEMA

Experimente buscar por:
- **Regina Duarte** - encontrará novelas como "Por Amor", "Vale Tudo", "Roque Santeiro"
- **Tony Ramos** - suas diversas participações
- **Fernanda Montenegro** - toda sua filmografia na Globo
- **Glória Pires** - suas novelas
- Qualquer ator/atriz que você lembre!

---

## 📊 COMO FUNCIONA O ARQUIVO RTF

O script `importar_elencos.py` faz o seguinte:

1. **Lê o arquivo RTF** (formato de texto rico)
2. **Identifica os títulos** (marcados em negrito no RTF)
3. **Extrai os nomes** do elenco de cada produção
4. **Decodifica caracteres especiais** (ã, é, ç, etc.)
5. **Insere tudo no banco SQLite** de forma organizada

---

## ⚙️ ESTRUTURA DO BANCO CRIADO

Após a importação, seu banco terá:

**Tabela `producoes`:**
- 337 novelas/minisséries

**Tabela `atores`:**
- 4.669 atores únicos (sem duplicatas)

**Tabela `elenco`:**
- 15.387 registros ligando atores às produções

---

## 🔄 REIMPORTANDO DADOS

Se quiser limpar e reimportar:

```bash
# Remove o banco antigo
rm novelas_globo.db

# Recria o banco vazio
python criar_banco.py

# Importa novamente
python importar_elencos.py
```

---

## 📝 NOTAS IMPORTANTES

✅ O script já está configurado para ler o arquivo `elencos.rtf` automaticamente  
✅ Caracteres especiais (acentos) são tratados corretamente  
✅ Atores duplicados são ignorados automaticamente (só entra uma vez)  
✅ O banco SQLite não precisa de servidor - é só um arquivo  

---

## 🎬 PRONTO PARA USAR!

Agora você tem um sistema completo de busca com **TODOS os seus elencos da Globo**!

Digite o nome de qualquer ator e veja instantaneamente todas as produções dele! 🚀
