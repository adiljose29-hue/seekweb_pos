from decimal import Decimal

class Calculos:
    @staticmethod
    def calcular_iva(valor, taxa_iva):
        """Calcula valor do IVA"""
        if taxa_iva == 0:
            return Decimal('0')
        return (valor * Decimal(str(taxa_iva))) / 100
    
    @staticmethod
    def calcular_total_com_iva(valor, taxa_iva):
        """Calcula total com IVA incluído"""
        iva = Calculos.calcular_iva(valor, taxa_iva)
        return valor + iva
    
    @staticmethod
    def calcular_iva_por_produto(preco_unitario, quantidade, taxa_iva):
        """Calcula IVA específico para cada produto"""
        subtotal = preco_unitario * quantidade
        return Calculos.calcular_iva(subtotal, taxa_iva)
    
    @staticmethod
    def calcular_subtotal_com_iva(preco_unitario, quantidade, taxa_iva):
        """Calcula subtotal com IVA incluído"""
        subtotal_sem_iva = preco_unitario * quantidade
        iva = Calculos.calcular_iva(subtotal_sem_iva, taxa_iva)
        return subtotal_sem_iva + iva
    
    @staticmethod
    def aplicar_desconto(valor, desconto_percentual):
        """Aplica desconto percentual"""
        if desconto_percentual == 0:
            return valor
        return valor * (1 - Decimal(str(desconto_percentual)) / 100)
    
    @staticmethod
    def calcular_troco(valor_pago, valor_devido):
        """Calcula troco"""
        return max(Decimal('0'), valor_pago - valor_devido)
    
    @staticmethod
    def calcular_pontos_fidelidade(valor_compra):
        """Calcula pontos de fidelidade (1 ponto por cada 100 Kz)"""
        return int(valor_compra / 100)
    
    @staticmethod
    def formatar_moeda(valor, moeda="Kz"):
        """Formata valor para exibição monetária"""
        return f"{float(valor):.2f} {moeda}"