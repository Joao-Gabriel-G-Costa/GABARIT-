import sqlite3

def conectar_ao_banco():
    """Conecta ao banco de dados SQLite e retorna a conexão e o cursor."""
    try:
        # Conecta ao banco de dados BANCOGABARIBOT (o arquivo banco.db)
        conn = sqlite3.connect("BANCOGABARIBOT.db")  # Alterado para seu banco SQLite
        cursor = conn.cursor()
        print('Conexão bem-sucedida!')
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None, None

def fechar_conexao(conn, cursor):
    """Fecha a conexão e o cursor do banco de dados."""
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
        print('Conexão encerrada.')


def main():
    conn, cursor = conectar_ao_banco()
    if conn is not None and cursor is not None:
        try:
            nome = input('digite o nome : ')
            senha = input('digite a senha')
           
            sql = "INSERT INTO usuario (usu_usuario, usu_senha) VALUES (%s, %s)"
            val = (nome, senha)
            
            cursor.execute(sql,val)
            conn.commit()
            
            print('deu certo')
        except Error as e:
            print(f"Erro ao executar a consulta: {e}")
        finally:
            fechar_conexao(conn, cursor)

if __name__ == "__main__":
    main()