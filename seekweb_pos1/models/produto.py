from core.database import Database
from decimal import Decimal

class Produto:
    def __init__(self, db: Database):
        self.db = db
    
    def obter_por_codigo_barras(self, codigo_barras):
        """Obtém produto por código de barras"""
        query = """
        SELECT p.*, t.taxa as taxa_iva, c.nome as categoria_nome
        FROM produtos p 
        LEFT JOIN taxas_iva t ON p.taxa_iva_id = t.id 
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.codigo_barras = %s AND p.ativo = 1
        """
        result = self.db.execute_query(query, (codigo_barras,))
        return result[0] if result else None
    
    def obter_por_id(self, produto_id):
        """Obtém produto por ID"""
        query = """
        SELECT p.*, t.taxa as taxa_iva, c.nome as categoria_nome
        FROM produtos p 
        LEFT JOIN taxas_iva t ON p.taxa_iva_id = t.id 
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = %s AND p.ativo = 1
        """
        result = self.db.execute_query(query, (produto_id,))
        return result[0] if result else None
    
    def obter_todos(self, filtro=None):
        """Obtém todos os produtos com filtro opcional"""
        query = """
        SELECT p.*, t.taxa as taxa_iva, c.nome as categoria_nome
        FROM produtos p 
        LEFT JOIN taxas_iva t ON p.taxa_iva_id = t.id 
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.ativo = 1
        """
        params = []
        
        if filtro:
            query += " AND (p.nome LIKE %s OR p.codigo_barras LIKE %s OR p.referencia LIKE %s)"
            params = [f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"]
        
        query += " ORDER BY p.nome"
        return self.db.execute_query(query, params)
    
    def verificar_stock(self, produto_id, quantidade):
        """Verifica se há stock suficiente"""
        produto = self.obter_por_id(produto_id)
        if produto and produto['stock'] >= quantidade:
            return True
        return False
    
    def atualizar_stock(self, produto_id, quantidade):
        """Atualiza stock do produto"""
        query = "UPDATE produtos SET stock = stock - %s WHERE id = %s AND stock >= %s"
        result = self.db.execute_insert(query, (quantidade, produto_id, quantidade))
        return result is not None
    
    def obter_stock_atual(self, produto_id):
        """Obtém stock atual do produto"""
        query = "SELECT stock FROM produtos WHERE id = %s"
        result = self.db.execute_query(query, (produto_id,))
        return result[0]['stock'] if result else 0