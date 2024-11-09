import sqlite3

connection = sqlite3.connect('alimentos.db')  # Renomeie o arquivo para refletir a mudança
cursor = connection.cursor()

# Criação da tabela com um novo campo 'categoria'
cursor.execute('''
    CREATE TABLE alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,  -- Tipo da fruta ou vegetal (ex: "maçã", "cenoura")
        cor TEXT NOT NULL,
        mes_colheita TEXT NOT NULL,
        categoria TEXT NOT NULL  -- Campo para diferenciar entre 'fruta' e 'vegetal'
    )
''')

connection.commit()
connection.close()