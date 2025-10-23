import sqlite3
import os
import csv
import codecs 

DB_FILE = "fornecedores.db"
CSV_FILE = "fornecedores.csv" 

# 1. VERIFICA SE O ARQUIVO CSV EXISTE
if not os.path.exists(CSV_FILE):
    print(f"ERRO CRÍTICO: Arquivo '{CSV_FILE}' não encontrado!")
    print("Por favor, exporte os 40.000 fornecedores para este arquivo antes de continuar.")
    print("LEMBRE-SE de salvar como 'CSV (UTF-8)'.")
    exit()

# 2. REMOVE O BANCO DE DADOS ANTIGO, SE EXISTIR
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Arquivo '{DB_FILE}' antigo removido.")

# 3. LEITURA E PROCESSAMENTO DO CSV
try:
    print(f"Lendo dados de '{CSV_FILE}'... (Isso pode levar alguns segundos)")
    with codecs.open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        
        # --- MODIFICAÇÃO ---
        # A linha "next(reader, None)" foi REMOVIDA
        # pois você já apagou o cabeçalho do arquivo.
            
        # O CSV tem: (row[0] = codigo, row[1] = nome)
        # O Banco espera: (nome, codigo)
        # Por isso usamos (row[1], row[0])
        lista_fornecedores = []
        for row in reader:
            if row and len(row) == 2:
                lista_fornecedores.append((row[1], row[0])) # Colunas invertidas
        # --- FIM DA MODIFICAÇÃO ---
    
    if not lista_fornecedores:
        print("ERRO: O arquivo CSV está vazio ou em formato inválido.")
        exit()
        
    print(f"Sucesso: {len(lista_fornecedores)} fornecedores lidos do CSV.")

except Exception as e:
    print(f"Ocorreu um erro ao ler o CSV: {e}")
    print("Verifique se o arquivo está salvo como UTF-8.")
    exit()

# 4. CRIAÇÃO E INSERÇÃO NO BANCO DE DADOS SQLITE
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Banco de dados '{DB_FILE}' criado.")

    cursor.execute("""
    CREATE TABLE fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        codigo TEXT NOT NULL UNIQUE
    );
    """)
    print("Tabela 'fornecedores' criada.")

    print(f"Inserindo {len(lista_fornecedores)} registros no banco... (Aguarde)")
    
    cursor.executemany("INSERT INTO fornecedores (nome, codigo) VALUES (?, ?)", lista_fornecedores)
    conn.commit()
    print(f"Sucesso! {cursor.rowcount} fornecedores foram inseridos no banco.")

    print("Criando índice de busca...")
    cursor.execute("CREATE INDEX idx_nome ON fornecedores (nome);")
    print("Índice de busca por nome foi criado.")

except sqlite3.IntegrityError as e:
    print(f"ERRO DE INTEGRIDADE: {e}")
    print("Isso geralmente significa que há 'códigos' duplicados no seu arquivo CSV.")
except sqlite3.Error as e:
    print(f"Ocorreu um erro do SQLite: {e}")
finally:
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")