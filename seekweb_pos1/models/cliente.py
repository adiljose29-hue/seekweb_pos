from core.database import Database

class Cliente:
    def __init__(self, db: Database):
        self.db = db
    
    def obter_por_codigo_cartao(self, codigo_cartao):
        """Obtém cliente por código do cartão"""
        query = "SELECT * FROM clientes WHERE codigo_cartao = %s AND ativo = 1"
        result = self.db.execute_query(query, (codigo_cartao,))
        return result[0] if result else None
    
    def autenticar_cartao(self, codigo_cartao, senha):
        """Autentica cliente por cartão e senha"""
        query = "SELECT * FROM clientes WHERE codigo_cartao = %s AND senha_cartao = %s AND ativo = 1"
        result = self.db.execute_query(query, (codigo_cartao, senha))
        return result[0] if result else None
    
    def adicionar_pontos(self, cliente_id, pontos):
        """Adiciona pontos de fidelidade ao cliente"""
        query = "UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + %s WHERE id = %s"
        return self.db.execute_insert(query, (pontos, cliente_id))