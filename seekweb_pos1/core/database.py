import mysql.connector
from mysql.connector import Error
import logging

class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config.get('Database', 'host'),
                user=self.config.get('Database', 'user'),
                password=self.config.get('Database', 'password'),
                database=self.config.get('Database', 'database'),
                port=self.config.getint('Database', 'port')
            )
            print("✅ Conectado à base de dados MySQL")
        except Error as e:
            print(f"❌ Erro ao conectar à base de dados: {e}")
            raise
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Erro na query: {e}")
            return None
    
    def execute_insert(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"❌ Erro no insert: {e}")
            self.connection.rollback()
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()