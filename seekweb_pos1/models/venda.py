from core.database import Database
from decimal import Decimal
import datetime
import traceback
from utils.calculos import Calculos
from models.produto import Produto

class Venda:
    def __init__(self, db: Database):
        self.db = db
    
    def criar_venda(self, dados_venda):
        """Cria uma nova venda com todos os dados - Versão Robusta"""
        try:
            print("🔄 Iniciando criação de venda...")
            
            # Validar dados obrigatórios
            campos_obrigatorios = ['empresa_id', 'caixa_id', 'usuario_id', 'total_sem_iva', 'total_iva', 'total_com_iva']
            for campo in campos_obrigatorios:
                if campo not in dados_venda or dados_venda[campo] is None:
                    print(f"❌ Campo obrigatório faltando: {campo}")
                    return None, None
            
            # Gerar número da venda
            numero_venda = f"V{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"📋 Número da venda gerado: {numero_venda}")
            
            # Tratar cliente_id - garantir que seja None se não fornecido
            cliente_id = dados_venda.get('cliente_id')
            if cliente_id in ['', None]:
                cliente_id = None
            
            print(f"📊 Dados para inserção:")
            print(f"   Empresa: {dados_venda['empresa_id']}")
            print(f"   Caixa: {dados_venda['caixa_id']}")
            print(f"   Usuário: {dados_venda['usuario_id']}")
            print(f"   Cliente: {cliente_id}")
            print(f"   Total sem IVA: {dados_venda['total_sem_iva']}")
            print(f"   Total IVA: {dados_venda['total_iva']}")
            print(f"   Total com IVA: {dados_venda['total_com_iva']}")
            
            query = """
            INSERT INTO vendas (empresa_id, caixa_id, usuario_id, cliente_id, numero_venda, 
                               total_sem_iva, total_iva, total_com_iva, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'paga')
            """
            
            params = (
                dados_venda['empresa_id'], 
                dados_venda['caixa_id'], 
                dados_venda['usuario_id'], 
                cliente_id,
                numero_venda, 
                float(dados_venda['total_sem_iva']), 
                float(dados_venda['total_iva']), 
                float(dados_venda['total_com_iva'])
            )
            
            print("💾 Executando INSERT na tabela vendas...")
            venda_id = self.db.execute_insert(query, params)
            
            if venda_id is None:
                print("❌ ERRO: venda_id retornou None após inserção")
                # Tentar ver qual foi o erro
                try:
                    # Verificar se a venda foi inserida mesmo com None
                    venda_check = self.db.execute_query(
                        "SELECT id FROM vendas WHERE numero_venda = %s", 
                        (numero_venda,)
                    )
                    if venda_check:
                        venda_id = venda_check[0]['id']
                        print(f"⚠️  Venda foi inserida com ID: {venda_id}, mas execute_insert retornou None")
                    else:
                        print("❌ Venda não foi inserida na base de dados")
                        return None, None
                except Exception as check_error:
                    print(f"❌ Erro ao verificar inserção: {check_error}")
                    return None, None
            
            print(f"✅ Venda criada com sucesso: ID {venda_id}, Número {numero_venda}")
            return venda_id, numero_venda
            
        except Exception as e:
            print(f"❌ Erro crítico ao criar venda: {e}")
            traceback.print_exc()
            return None, None
    
    def adicionar_itens(self, venda_id, itens):
        """Adiciona múltiplos itens à venda - Versão Robusta"""
        try:
            print(f"🔄 Adicionando {len(itens)} itens à venda {venda_id}...")
            
            if not itens:
                print("❌ Nenhum item para adicionar")
                return False
            
            if venda_id is None:
                print("❌ venda_id é None")
                return False
            
            for index, item in enumerate(itens):
                print(f"📦 Processando item {index + 1}: {item}")
                
                # Validar campos do item
                campos_item = ['produto_id', 'quantidade', 'preco_unitario', 'taxa_iva_id', 'valor_iva', 'subtotal']
                for campo in campos_item:
                    if campo not in item or item[campo] is None:
                        print(f"❌ Campo {campo} faltando no item {index}")
                        return False
                
                query = """
                INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario, 
                                        taxa_iva_id, valor_iva, subtotal, desconto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                params = (
                    venda_id, 
                    item['produto_id'], 
                    item['quantidade'], 
                    float(item['preco_unitario']), 
                    item['taxa_iva_id'], 
                    float(item['valor_iva']), 
                    float(item['subtotal']), 
                    float(item.get('desconto', 0))
                )
                
                print(f"💾 Inserindo item {index + 1}...")
                result = self.db.execute_insert(query, params)
                
                if result is None:
                    print(f"❌ Falha ao inserir item {index + 1}")
                    # Tentar continuar com os outros itens?
                    continue
            
            print(f"✅ {len(itens)} itens processados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar itens: {e}")
            traceback.print_exc()
            return False
    
    def adicionar_pagamentos(self, venda_id, pagamentos):
        """Adiciona múltiplos pagamentos à venda - Versão Robusta"""
        try:
            print(f"🔄 Adicionando {len(pagamentos)} pagamentos à venda {venda_id}...")
            
            if not pagamentos:
                print("❌ Nenhum pagamento para adicionar")
                return False
            
            if venda_id is None:
                print("❌ venda_id é None")
                return False
            
            for index, pagamento in enumerate(pagamentos):
                print(f"💳 Processando pagamento {index + 1}: {pagamento}")
                
                # Validar campos do pagamento
                if 'forma_pagamento_id' not in pagamento or pagamento['forma_pagamento_id'] is None:
                    print(f"❌ forma_pagamento_id faltando no pagamento {index}")
                    return False
                
                if 'valor' not in pagamento or pagamento['valor'] is None:
                    print(f"❌ valor faltando no pagamento {index}")
                    return False
                
                query = """
                INSERT INTO venda_pagamentos (venda_id, forma_pagamento_id, valor, troco, referencia)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                params = (
                    venda_id, 
                    pagamento['forma_pagamento_id'], 
                    float(pagamento['valor']),
                    float(pagamento.get('troco', 0)), 
                    str(pagamento.get('referencia', ''))
                )
                
                print(f"💾 Inserindo pagamento {index + 1}...")
                result = self.db.execute_insert(query, params)
                
                if result is None:
                    print(f"❌ Falha ao inserir pagamento {index + 1}")
                    continue
            
            print(f"✅ {len(pagamentos)} pagamentos processados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar pagamentos: {e}")
            traceback.print_exc()
            return False
    
    def processar_venda_completa(self, dados_venda, itens, pagamentos):
        """Processa uma venda completa (transação) - Versão Super Robusta"""
        try:
            print("🎯 INICIANDO PROCESSAMENTO COMPLETO DA VENDA")
            print("=" * 50)
            
            # Validação rigorosa
            if not itens:
                return False, "Nenhum item no carrinho"
            
            if not pagamentos:
                return False, "Nenhum pagamento especificado"
            
            print(f"📦 Itens: {len(itens)}")
            print(f"💳 Pagamentos: {len(pagamentos)}")
            print(f"📊 Dados venda: {dados_venda}")
            
            # 1. Criar venda
            venda_id, numero_venda = self.criar_venda(dados_venda)
            
            if venda_id is None:
                return False, "Falha crítica: não foi possível criar o registro da venda"
            
            print(f"✅ Fase 1 concluída: Venda {numero_venda} criada com ID {venda_id}")
            
            # 2. Adicionar itens
            if not self.adicionar_itens(venda_id, itens):
                # Tentar limpar a venda criada
                self._limpar_venda_falha(venda_id)
                return False, "Falha ao adicionar itens à venda"
            
            print("✅ Fase 2 concluída: Itens adicionados")
            
            # 3. Adicionar pagamentos
            if not self.adicionar_pagamentos(venda_id, pagamentos):
                # Tentar limpar a venda criada
                self._limpar_venda_falha(venda_id)
                return False, "Falha ao adicionar pagamentos"
            
            print("✅ Fase 3 concluída: Pagamentos processados")
            
            # 4. Atualizar stock (opcional - pode continuar mesmo com falha)
            produto_model = Produto(self.db)
            stock_errors = []
            
            for item in itens:
                try:
                    sucesso = produto_model.atualizar_stock(item['produto_id'], item['quantidade'])
                    if not sucesso:
                        stock_errors.append(f"Produto ID {item['produto_id']}")
                        print(f"⚠️  Aviso: Não foi possível atualizar stock do produto {item['produto_id']}")
                except Exception as e:
                    stock_errors.append(f"Produto ID {item['produto_id']}: {e}")
                    print(f"⚠️  Erro ao atualizar stock: {e}")
            
            if stock_errors:
                print(f"⚠️  Avisos de stock: {stock_errors}")
                # Não falhar a venda por erro de stock, apenas registrar
            
            print("✅ Fase 4 concluída: Stock atualizado")
            print("🎉 VENDA PROCESSADA COM SUCESSO!")
            
            return True, numero_venda
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO NO PROCESSAMENTO: {e}")
            traceback.print_exc()
            return False, f"Erro crítico: {str(e)}"
    
    def obter_detalhes_venda_por_numero(self, numero_venda):
        """Obtém detalhes completos de uma venda pelo número"""
        # Venda principal
        query_venda = """
        SELECT v.*, u.nome as vendedor, c.nome as cliente_nome, c.codigo_cartao
        FROM vendas v
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.numero_venda = %s
        """
        venda = self.db.execute_query(query_venda, (numero_venda,))
        
        if not venda:
            return None
        
        venda_id = venda[0]['id']
        
        # Itens da venda
        query_itens = """
        SELECT vi.*, p.nome as produto_nome, p.codigo_barras, t.taxa
        FROM venda_itens vi
        JOIN produtos p ON vi.produto_id = p.id
        JOIN taxas_iva t ON vi.taxa_iva_id = t.id
        WHERE vi.venda_id = %s
        """
        itens = self.db.execute_query(query_itens, (venda_id,))
        
        # Pagamentos
        query_pagamentos = """
        SELECT vp.*, fp.nome as forma_pagamento
        FROM venda_pagamentos vp
        JOIN formas_pagamento fp ON vp.forma_pagamento_id = fp.id
        WHERE vp.venda_id = %s
        """
        pagamentos = self.db.execute_query(query_pagamentos, (venda_id,))
        
        return {
            'venda': venda[0],
            'itens': itens,
            'pagamentos': pagamentos
        }
    
    def _limpar_venda_falha(self, venda_id):
        """Limpa uma venda que falhou no processamento"""
        try:
            if venda_id:
                print(f"🧹 Limpando venda falha ID {venda_id}...")
                self.db.execute_insert("DELETE FROM venda_pagamentos WHERE venda_id = %s", (venda_id,))
                self.db.execute_insert("DELETE FROM venda_itens WHERE venda_id = %s", (venda_id,))
                self.db.execute_insert("DELETE FROM vendas WHERE id = %s", (venda_id,))
                print("✅ Venda falha limpa")
        except Exception as e:
            print(f"❌ Erro ao limpar venda falha: {e}")
            