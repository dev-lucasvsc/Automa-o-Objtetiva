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
    try:
        os.remove(DB_FILE)
        print(f"Arquivo '{DB_FILE}' antigo removido.")
    except Exception as e:
        print(f"ERRO ao tentar remover o banco de dados antigo: {e}")
        print("Verifique se o arquivo não está sendo usado por outro programa e tente novamente.")
        exit()


# 3. LEITURA E PROCESSAMENTO DO CSV
try:
    print(f"Lendo dados de '{CSV_FILE}'... (Isso pode levar alguns segundos)")
    lista_fornecedores = []
    with codecs.open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        # ****** CORREÇÃO: Adicionado delimiter=';' ******
        reader = csv.reader(f, delimiter=';')

        # O cabeçalho já foi removido manualmente do CSV, então não precisamos pular a primeira linha.

        for i, row in enumerate(reader):
            # Verifica se a linha não está vazia e tem exatamente 2 colunas após a divisão pelo ';'
            if row and len(row) == 2:
                codigo = row[0].strip()
                nome = row[1].strip()
                if codigo and nome: # Garante que código e nome não estão vazios após strip()
                    # O Banco espera: (nome, codigo)
                    lista_fornecedores.append((nome, codigo))
                else:
                    print(f"AVISO: Linha {i+1} ignorada - Código ou Nome vazio após processamento: {row}")
            elif row: # Se a linha existe mas não tem 2 colunas
                 print(f"AVISO: Linha {i+1} ignorada - Formato inesperado (esperado: codigo;nome): {row}")
            # Linhas vazias são ignoradas silenciosamente

    if not lista_fornecedores:
        print("ERRO CRÍTICO: Nenhum fornecedor válido encontrado no arquivo CSV.")
        print("Verifique se o arquivo CSV está no formato 'codigo;nome' e não está vazio.")
        exit()

    print(f"Sucesso: {len(lista_fornecedores)} fornecedores válidos lidos do CSV.")

except FileNotFoundError:
    print(f"ERRO CRÍTICO: Arquivo '{CSV_FILE}' não encontrado!")
    exit()
except Exception as e:
    print(f"Ocorreu um erro ao ler ou processar o CSV: {e}")
    print("Verifique se o arquivo está salvo como UTF-8 e se o delimitador é ';'.")
    exit()

# 4. CRIAÇÃO E INSERÇÃO NO BANCO DE DADOS SQLITE
conn = None # Inicializa conn como None
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Banco de dados '{DB_FILE}' criado/conectado.")

    # Apaga a tabela antiga se existir (garante uma recriação limpa)
    cursor.execute("DROP TABLE IF EXISTS fornecedores;")
    print("Tabela 'fornecedores' antiga (se existia) removida.")

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

    # Apaga índice antigo se existir
    cursor.execute("DROP INDEX IF EXISTS idx_nome;")
    print("Índice 'idx_nome' antigo (se existia) removido.")

    print("Criando índice de busca...")
    cursor.execute("CREATE INDEX idx_nome ON fornecedores (nome);")
    print("Índice de busca por nome ('idx_nome') foi criado.")

except sqlite3.IntegrityError as e:
    print(f"ERRO DE INTEGRIDADE: {e}")
    print("Isso geralmente significa que há 'códigos' duplicados no seu arquivo CSV.")
except sqlite3.Error as e:
    print(f"Ocorreu um erro do SQLite: {e}")
finally:
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")

print("\n--- Configuração do Banco de Dados Concluída ---")