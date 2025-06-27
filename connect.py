import psycopg2 as pg
from psycopg2 import Error
from dotenv import load_dotenv
from datetime import datetime
import os, traceback

load_dotenv()

def connect(args):
    if args.clear: # Limpa o log se o argumento for atribuido
        with open('logs/logs.txt', 'w', encoding='utf-8') as arquivo_log:
            arquivo_log.write("")
    save_log("Conectando com o banco de dados...")
    try:
        conecta = pg.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('HOST'),
            port=os.getenv('PORT'),
            database=os.getenv('DATABASE')
        )
        # print("Conectado com sucesso!")
        save_log("Conectado com sucesso!")
        return conecta
    except Error as e:
        erro_completo = traceback.format_exc()
        # print(f"Falha ao conectar ao banco de dados: {e}")
        save_log(f"Falha ao conectar ao banco de dados: {e}")
        save_log(f"{erro_completo}")
        quit()

def save_log(texto):
    with open('logs/logs.txt', 'a', encoding='utf-8') as arquivo_log:
        data_atual = datetime.now()
        data_formatada = data_atual.strftime('%d-%m-%Y - %H:%M:%S.%f')
        arquivo_log.write(f"[ {data_formatada} ] ----- {texto}\n")

def disconnect(conecta):
    if conecta:
        conecta.close()