from core.database import Database
import logging

class Usuario:
    def __init__(self, db: Database):
        self.db = db
    
    def autenticar(self, email, senha):
        """Autentica usuário no sistema"""
        query = """
        SELECT u.*, n.nome as nivel_nome, n.permissoes 
        FROM usuarios u 
        JOIN niveis_usuario n ON u.nivel_id = n.id 
        WHERE u.email = %s AND u.senha = %s AND u.ativo = 1
        """
        result = self.db.execute_query(query, (email, senha))
        return result[0] if result else None
    
    def obter_por_codigo_barras(self, codigo_barras):
        """Obtém usuário por código de barras"""
        query = "SELECT * FROM usuarios WHERE codigo_barras = %s AND ativo = 1"
        result = self.db.execute_query(query, (codigo_barras,))
        return result[0] if result else None
    
    def obter_todos(self):
        """Obtém todos os usuários"""
        query = """
        SELECT u.*, n.nome as nivel_nome 
        FROM usuarios u 
        JOIN niveis_usuario n ON u.nivel_id = n.id 
        WHERE u.ativo = 1
        """
        return self.db.execute_query(query)
    
    def criar(self, dados):
        """Cria novo usuário"""
        query = """
        INSERT INTO usuarios (empresa_id, nivel_id, nome, email, senha, codigo_barras, ativo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_insert(query, (
            dados['empresa_id'], dados['nivel_id'], dados['nome'],
            dados['email'], dados['senha'], dados.get('codigo_barras'), 1
        ))