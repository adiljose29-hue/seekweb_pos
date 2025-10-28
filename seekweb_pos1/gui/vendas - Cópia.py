from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QMessageBox, QFrame,
                             QTabWidget, QGroupBox, QGridLayout, QHeaderView,  # Adicionar QHeaderView aqui
                             QShortcut, QDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QKeySequence

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QMessageBox, QFrame,
                             QTabWidget, QGroupBox, QGridLayout, QHeaderView,
                             QShortcut)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QKeySequence
from decimal import Decimal
import json
from models.produto import Produto
from models.venda import Venda
from models.cliente import Cliente
from utils.calculos import Calculos
from utils.scanner import Scanner
from gui.pagamentos import DialogMultiplosPagamentos
from utils.recibo import GeradorRecibos


class VendasWindow(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        # CORREÇÃO: Inicializar usuario_atual como None e depois atualizar
        self._usuario_atual = None
        self.carrinho = []
        self.produto_model = Produto(db)
        self.venda_model = Venda(db)
        self.cliente_model = Cliente(db)
        self.scanner = Scanner(parent.config) if parent and hasattr(parent, 'config') else None
        self.codigo_scanner_buffer = ""
        self.setup_ui()
        self.setup_scanner()
        self.carregar_produtos_reais()
        
        # DEBUG
        print(f"🔍 VendasWindow init completo - usuario_atual: {self.usuario_atual}")
    
    @property
    def usuario_atual(self):
        """Propriedade para acessar usuario_atual de forma segura"""
        return self._usuario_atual
    
    @usuario_atual.setter
    def usuario_atual(self, value):
        """Setter para usuario_atual"""
        self._usuario_atual = value
        print(f"🔍 VendasWindow - usuario_atual definido: {value['nome'] if value else 'None'}")
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        
        # Left Panel - Produtos (80% da tela)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Título da seção
        titulo_label = QLabel("🎯 ÁREA DE VENDAS")
        titulo_label.setFont(QFont("Arial", 16, QFont.Bold))
        titulo_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        titulo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(titulo_label)
        
        # Scanner e Busca
        scanner_busca_layout = QHBoxLayout()
        
        # Grupo do Scanner
        scanner_group = QGroupBox("📷 Scanner de Código de Barras")
        scanner_layout = QVBoxLayout()
        
        self.scanner_status = QLabel("🟡 Scanner: Pronto para uso")
        self.scanner_status.setStyleSheet("font-weight: bold; padding: 5px;")
        
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Clique aqui e use o scanner ou digite o código...")
        self.scanner_input.returnPressed.connect(self.processar_codigo_scanner)
        
        scanner_btn_layout = QHBoxLayout()
        self.btn_ativar_scanner = QPushButton("🎯 Ativar Scanner")
        self.btn_ativar_scanner.clicked.connect(self.ativar_scanner)
        self.btn_desativar_scanner = QPushButton("⏹️ Desativar")
        self.btn_desativar_scanner.clicked.connect(self.desativar_scanner)
        self.btn_desativar_scanner.setEnabled(False)
        
        scanner_btn_layout.addWidget(self.btn_ativar_scanner)
        scanner_btn_layout.addWidget(self.btn_desativar_scanner)
        
        scanner_layout.addWidget(self.scanner_status)
        scanner_layout.addWidget(self.scanner_input)
        scanner_layout.addLayout(scanner_btn_layout)
        scanner_group.setLayout(scanner_layout)
        
        # Grupo da Busca
        busca_group = QGroupBox("🔍 Buscar Produtos")
        busca_layout = QVBoxLayout()
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Digite nome, código ou referência do produto...")
        self.busca_input.textChanged.connect(self.filtrar_produtos)
        busca_layout.addWidget(self.busca_input)
        busca_group.setLayout(busca_layout)
        
        scanner_busca_layout.addWidget(scanner_group, 2)
        scanner_busca_layout.addWidget(busca_group, 1)
        left_layout.addLayout(scanner_busca_layout)
        
        # Grid de produtos
        produtos_group = QGroupBox("📦 Produtos Disponíveis")
        produtos_layout = QVBoxLayout()
        
        # Container para a grid
        self.produtos_container = QWidget()
        self.produtos_grid = QGridLayout(self.produtos_container)
        produtos_layout.addWidget(self.produtos_container)
        
        produtos_group.setLayout(produtos_layout)
        left_layout.addWidget(produtos_group)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        self.btn_limpar = QPushButton("🗑️ Limpar Carrinho")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_limpar.clicked.connect(self.limpar_carrinho)
        
        self.btn_finalizar = QPushButton("💰 Finalizar Venda")
        self.btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.btn_finalizar.clicked.connect(self.finalizar_venda)
        
        self.btn_logout = QPushButton("🚪 Sair")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #636e72;
            }
        """)
        self.btn_logout.clicked.connect(self.logout_requested.emit)
        
        acoes_layout.addWidget(self.btn_limpar)
        acoes_layout.addWidget(self.btn_finalizar)
        acoes_layout.addWidget(self.btn_logout)
        
        left_layout.addLayout(acoes_layout)
        
        # Right Panel - Carrinho e Total
        right_widget = QWidget()
        right_widget.setMaximumWidth(500)
        right_layout = QVBoxLayout(right_widget)
        
        # Informações do vendedor
        vendedor_group = QGroupBox("👤 Vendedor")
        vendedor_layout = QVBoxLayout()
        if self.usuario_atual:
            vendedor_label = QLabel(f"Vendedor: {self.usuario_atual['nome']}")
            vendedor_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            vendedor_layout.addWidget(vendedor_label)
        vendedor_group.setLayout(vendedor_layout)
        right_layout.addWidget(vendedor_group)
        
        # Cliente
        cliente_group = QGroupBox("👥 Cliente (Opcional)")
        cliente_layout = QVBoxLayout()
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("Código do cartão cliente...")
        cliente_layout.addWidget(QLabel("Cartão Cliente:"))
        cliente_layout.addWidget(self.cliente_input)
        
        cliente_group.setLayout(cliente_layout)
        right_layout.addWidget(cliente_group)
        
        # Carrinho
        carrinho_group = QGroupBox("🛒 Carrinho de Compras")
        carrinho_layout = QVBoxLayout()
        
        self.carrinho_table = QTableWidget()
        self.carrinho_table.setColumnCount(5)
        self.carrinho_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço", "IVA", "Total"])
        header = self.carrinho_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        carrinho_layout.addWidget(self.carrinho_table)
        carrinho_group.setLayout(carrinho_layout)
        right_layout.addWidget(carrinho_group)
        
        # Total
        total_group = QGroupBox("💳 Totalização")
        total_layout = QVBoxLayout()
        
        self.lbl_subtotal = QLabel("Subtotal: 0.00 Kz")
        self.lbl_subtotal.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        
        self.lbl_iva = QLabel("IVA: 0.00 Kz")
        self.lbl_iva.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        
        self.lbl_total = QLabel("TOTAL: 0.00 Kz")
        self.lbl_total.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #2c3e50; background-color: #ecf0f1; padding: 10px; border-radius: 5px;")
        
        total_layout.addWidget(self.lbl_subtotal)
        total_layout.addWidget(self.lbl_iva)
        total_layout.addWidget(self.lbl_total)
        
        total_group.setLayout(total_layout)
        right_layout.addWidget(total_group)
        
        # Formas de Pagamento
        pagamento_group = QGroupBox("💵 Pagamento")
        pagamento_layout = QVBoxLayout()
        
        self.combo_pagamento = QComboBox()
        self.carregar_formas_pagamento()
        
        self.valor_pago_input = QLineEdit()
        self.valor_pago_input.setPlaceholderText("0.00")
        self.valor_pago_input.textChanged.connect(self.calcular_troco)
        
        self.lbl_troco = QLabel("Troco: 0.00 Kz")
        self.lbl_troco.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        pagamento_layout.addWidget(QLabel("Forma de Pagamento:"))
        pagamento_layout.addWidget(self.combo_pagamento)
        pagamento_layout.addWidget(QLabel("Valor Pago:"))
        pagamento_layout.addWidget(self.valor_pago_input)
        pagamento_layout.addWidget(self.lbl_troco)
        
        pagamento_group.setLayout(pagamento_layout)
        right_layout.addWidget(pagamento_group)
        
        # Adicionar widgets ao layout principal
        main_layout.addWidget(left_widget, 4)  # 80%
        main_layout.addWidget(right_widget, 1) # 20%
        self.setLayout(main_layout)
        
        # Configurar atalhos de teclado
        self.setup_shortcuts()
    
    def setup_scanner(self):
        """Configura o scanner"""
        if self.scanner:
            # Conectar sinal do scanner
            self.scanner.codigo_lido.connect(self.on_codigo_scanner_lido)
            print("✅ Scanner configurado e pronto")
        else:
            print("⚠️ Scanner não disponível")
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        # Foco no campo do scanner
        shortcut_scanner = QShortcut(QKeySequence("F2"), self)
        shortcut_scanner.activated.connect(self.focar_scanner)
        
        # Limpar carrinho
        shortcut_limpar = QShortcut(QKeySequence("Ctrl+L"), self)
        shortcut_limpar.activated.connect(self.limpar_carrinho)
        
        # Finalizar venda
        shortcut_venda = QShortcut(QKeySequence("F10"), self)
        shortcut_venda.activated.connect(self.finalizar_venda)
    
    def focar_scanner(self):
        """Coloca foco no campo do scanner"""
        self.scanner_input.setFocus()
        self.scanner_input.selectAll()
    
    def ativar_scanner(self):
        """Ativa o scanner"""
        if self.scanner:
            self.scanner.iniciar_leitura()
            self.scanner_status.setText("🟢 Scanner: Ativo e aguardando...")
            self.scanner_status.setStyleSheet("font-weight: bold; color: #27ae60; padding: 5px;")
            self.btn_ativar_scanner.setEnabled(False)
            self.btn_desativar_scanner.setEnabled(True)
            self.focar_scanner()
            QMessageBox.information(self, "Scanner Ativado", 
                                  "Scanner ativado com sucesso!\n\n"
                                  "Aponte o scanner para o código de barras ou use o campo de texto.\n"
                                  "Pressione F2 para focar no campo do scanner.")
    
    def desativar_scanner(self):
        """Desativa o scanner"""
        if self.scanner:
            self.scanner.parar_leitura()
            self.scanner_status.setText("🟡 Scanner: Desativado")
            self.scanner_status.setStyleSheet("font-weight: bold; color: #f39c12; padding: 5px;")
            self.btn_ativar_scanner.setEnabled(True)
            self.btn_desativar_scanner.setEnabled(False)
    
    def on_codigo_scanner_lido(self, codigo):
        """Processa código lido pelo scanner"""
        print(f"📦 Código recebido do scanner: {codigo}")
        
        # Atualizar interface na thread principal
        self.scanner_input.setText(codigo)
        self.processar_codigo_scanner()
    
    def processar_codigo_scanner(self):
        """Processa código digitado ou lido pelo scanner"""
        codigo = self.scanner_input.text().strip()
        
        if not codigo:
            return
        
        print(f"🔍 Procurando produto com código: {codigo}")
        
        # Buscar produto pelo código de barras
        produto = self.produto_model.obter_por_codigo_barras(codigo)
        
        if produto:
            print(f"✅ Produto encontrado: {produto['nome']}")
            self.adicionar_ao_carrinho(produto)
            self.scanner_input.clear()
            self.focar_scanner()  # Volta o foco para o scanner
        else:
            print(f"❌ Produto não encontrado para código: {codigo}")
            QMessageBox.warning(self, "Produto Não Encontrado", 
                              f"Nenhum produto encontrado com o código:\n{codigo}")
            self.scanner_input.selectAll()
            self.scanner_input.setFocus()
    
    def keyPressEvent(self, event):
        """Captura eventos de teclado para o scanner"""
        # Se o scanner estiver ativo e for um scanner USB/teclado
        if (self.scanner and 
            self.scanner.leitura_ativa and 
            event.text() and 
            event.text().isprintable()):
            
            # Acumular caracteres para scanners que emulam teclado
            self.codigo_scanner_buffer += event.text()
            
            # Se pressionou Enter, processa o código
            if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
                if self.codigo_scanner_buffer.strip():
                    self.scanner.simular_leitura_teclado(self.codigo_scanner_buffer.strip())
                    self.codigo_scanner_buffer = ""
        
        super().keyPressEvent(event)
    
    def carregar_formas_pagamento(self):
        """Carrega formas de pagamento no ComboBox - Versão Corrigida"""
        try:
            print("🔍 Carregando formas de pagamento...")
            
            # Limpar combo box primeiro
            self.combo_pagamento.clear()
            
            formas_pagamento = self.db.execute_query(
                "SELECT id, nome, codigo, aceita_troco FROM formas_pagamento WHERE ativo = 1 ORDER BY id"
            )
            
            print(f"📊 Formas de pagamento encontradas: {len(formas_pagamento)}")
            
            if formas_pagamento:
                for fp in formas_pagamento:
                    # CORREÇÃO: Garantir que todos os campos existem
                    fp_data = {
                        'id': fp['id'],
                        'nome': fp['nome'],
                        'codigo': fp['codigo'],
                        'aceita_troco': bool(fp.get('aceita_troco', False))
                    }
                    print(f"   ✅ Adicionando: {fp_data['nome']} (ID: {fp_data['id']})")
                    self.combo_pagamento.addItem(fp_data['nome'], fp_data)
            else:
                print("⚠️ Nenhuma forma de pagamento encontrada, adicionando padrão...")
                # Adicionar opções padrão em caso de erro
                formas_padrao = [
                    {'id': 1, 'nome': 'Dinheiro', 'codigo': 'DINHEIRO', 'aceita_troco': True},
                    {'id': 2, 'nome': 'Cartão Débito', 'codigo': 'CARTAO_DEBITO', 'aceita_troco': False},
                    {'id': 3, 'nome': 'Cartão Crédito', 'codigo': 'CARTAO_CREDITO', 'aceita_troco': False}
                ]
                
                for fp in formas_padrao:
                    self.combo_pagamento.addItem(fp['nome'], fp)
                    print(f"   ✅ Adicionando padrão: {fp['nome']}")
            
            # CORREÇÃO: Verificar se o combo box tem itens
            if self.combo_pagamento.count() == 0:
                print("❌ ERRO: Combo box de formas de pagamento vazio!")
                QMessageBox.critical(self, "Erro de Configuração", 
                                   "Não foi possível carregar as formas de pagamento.\n\n"
                                   "Verifique a conexão com a base de dados.")
            else:
                print(f"✅ Combo box carregado com {self.combo_pagamento.count()} itens")
                # Selecionar o primeiro item por padrão
                self.combo_pagamento.setCurrentIndex(0)
                current_data = self.combo_pagamento.currentData()
                print(f"✅ Item selecionado: {current_data}")
                    
        except Exception as e:
            print(f"❌ Erro ao carregar formas de pagamento: {e}")
            import traceback
            traceback.print_exc()
            
            # CORREÇÃO: Adicionar opções padrão em caso de erro
            self.combo_pagamento.clear()
            formas_padrao = [
                {'id': 1, 'nome': 'Dinheiro', 'codigo': 'DINHEIRO', 'aceita_troco': True},
                {'id': 2, 'nome': 'Cartão', 'codigo': 'CARTAO', 'aceita_troco': False}
            ]
            
            for fp in formas_padrao:
                self.combo_pagamento.addItem(fp['nome'], fp)
    
    # ... (os outros métodos permanecem os mesmos: carregar_produtos_reais, criar_botoes_produtos, 
    # adicionar_ao_carrinho, atualizar_carrinho, calcular_troco, limpar_carrinho, finalizar_venda, 
    # salvar_venda, filtrar_produtos, carregar_dados)
    
    def carregar_produtos_reais(self):
        """Carrega produtos reais da base de dados"""
        try:
            produtos = self.produto_model.obter_todos()
            self.criar_botoes_produtos(produtos)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {str(e)}")
    
    def criar_botoes_produtos(self, produtos):
        """Cria botões dos produtos baseado na base de dados"""
        # Limpar grid existente
        for i in reversed(range(self.produtos_grid.count())): 
            widget = self.produtos_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        if not produtos:
            no_products_label = QLabel("Nenhum produto encontrado")
            no_products_label.setAlignment(Qt.AlignCenter)
            self.produtos_grid.addWidget(no_products_label, 0, 0)
            return
        
        row, col = 0, 0
        max_cols = 4  # 4 colunas para melhor visualização
        
        for produto in produtos:
            # Calcular preço com IVA
            preco_com_iva = Calculos.calcular_total_com_iva(
                Decimal(str(produto['preco_venda'])), 
                produto['taxa_iva']
            )
            
            # Criar botão com informações do produto
            btn_text = f"{produto['nome']}\n{preco_com_iva:.2f} Kz\nStock: {produto['stock']}\nIVA: {produto['taxa_iva']}%"
            btn = QPushButton(btn_text)
            btn.setFixedSize(150, 100)
            btn.setToolTip(f"{produto['descricao'] or 'Sem descrição'}\nRef: {produto['referencia']}")
            
            # Cor baseada no stock
            if produto['stock'] <= 0:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffebee;
                        color: #c62828;
                        border: 2px solid #c62828;
                        border-radius: 8px;
                        padding: 5px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                """)
                btn.setEnabled(False)
            elif produto['stock'] <= 5:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #fff3e0;
                        color: #ef6c00;
                        border: 2px solid #ff9800;
                        border-radius: 8px;
                        padding: 5px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ffe0b2;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e8f5e8;
                        color: #2e7d32;
                        border: 2px solid #4caf50;
                        border-radius: 8px;
                        padding: 5px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c8e6c9;
                        border: 2px solid #2e7d32;
                    }
                """)
            
            # Conectar clique
            btn.clicked.connect(lambda checked, p=produto: self.adicionar_ao_carrinho(p))
            self.produtos_grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def adicionar_ao_carrinho(self, produto):
        """Adiciona produto ao carrinho com verificação de stock"""
        try:
            # Verificar stock
            if not self.produto_model.verificar_stock(produto['id'], 1):
                QMessageBox.warning(self, "Stock Insuficiente", 
                                  f"❌ Produto {produto['nome']} sem stock disponível!\n\nStock atual: {produto['stock']}")
                return
            
            # Verificar se produto já está no carrinho
            for item in self.carrinho:
                if item['id'] == produto['id']:
                    # Verificar stock para quantidade adicional
                    if not self.produto_model.verificar_stock(produto['id'], item['quantidade'] + 1):
                        QMessageBox.warning(self, "Stock Insuficiente", 
                                          f"❌ Stock insuficiente para {produto['nome']}!\n\nStock atual: {produto['stock']}\nQuantidade no carrinho: {item['quantidade']}")
                        return
                    item['quantidade'] += 1
                    self.atualizar_carrinho()
                    
                    # Feedback visual
                    QMessageBox.information(self, "Produto Adicionado", 
                                          f"✅ {produto['nome']}\nQuantidade: {item['quantidade']}\nPreço: {item['preco_venda']:.2f} Kz")
                    return
            
            # Adicionar novo item
            novo_item = {
                'id': produto['id'],
                'nome': produto['nome'],
                'preco_venda': Decimal(str(produto['preco_venda'])),
                'taxa_iva': produto['taxa_iva'],
                'taxa_iva_id': produto['taxa_iva_id'],
                'quantidade': 1,
                'stock_atual': produto['stock']
            }
            
            self.carrinho.append(novo_item)
            self.atualizar_carrinho()
            
            # Feedback visual
            QMessageBox.information(self, "Produto Adicionado", 
                                  f"✅ {produto['nome']}\nQuantidade: 1\nPreço: {produto['preco_venda']:.2f} Kz\nIVA: {produto['taxa_iva']}%")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar produto: {str(e)}")
    
    def atualizar_carrinho(self):
        """Atualiza tabela do carrinho e totais"""
        try:
            self.carrinho_table.setRowCount(len(self.carrinho))
            
            subtotal_sem_iva = Decimal('0')
            total_iva = Decimal('0')
            
            for row, item in enumerate(self.carrinho):
                # Calcular valores
                subtotal_item_sem_iva = item['preco_venda'] * item['quantidade']
                iva_item = Calculos.calcular_iva(subtotal_item_sem_iva, item['taxa_iva'])
                total_item = subtotal_item_sem_iva + iva_item
                
                subtotal_sem_iva += subtotal_item_sem_iva
                total_iva += iva_item
                
                # Adicionar à tabela
                self.carrinho_table.setItem(row, 0, QTableWidgetItem(item['nome']))
                self.carrinho_table.setItem(row, 1, QTableWidgetItem(str(item['quantidade'])))
                self.carrinho_table.setItem(row, 2, QTableWidgetItem(f"{item['preco_venda']:.2f} Kz"))
                self.carrinho_table.setItem(row, 3, QTableWidgetItem(f"{item['taxa_iva']}%"))
                self.carrinho_table.setItem(row, 4, QTableWidgetItem(f"{total_item:.2f} Kz"))
            
            total_geral = subtotal_sem_iva + total_iva
            
            self.lbl_subtotal.setText(f"Subtotal: {subtotal_sem_iva:.2f} Kz")
            self.lbl_iva.setText(f"IVA: {total_iva:.2f} Kz")
            self.lbl_total.setText(f"TOTAL: {total_geral:.2f} Kz")
            
            # Calcular troco
            self.calcular_troco()
            
        except Exception as e:
            print(f"Erro ao atualizar carrinho: {e}")
    
    def calcular_troco(self):
        """Calcula troco baseado no valor pago"""
        try:
            valor_pago_text = self.valor_pago_input.text().replace(',', '.').strip()
            if not valor_pago_text:
                self.lbl_troco.setText("Troco: 0.00 Kz")
                return
                
            valor_pago = Decimal(valor_pago_text)
            total_text = self.lbl_total.text().split(": ")[1].replace(" Kz", "").replace(',', '.').strip()
            total_geral = Decimal(total_text)
            
            troco = max(Decimal('0'), valor_pago - total_geral)
            self.lbl_troco.setText(f"Troco: {troco:.2f} Kz")
            
        except Exception as e:
            self.lbl_troco.setText("Troco: 0.00 Kz")
    
    def limpar_carrinho(self):
        """Limpa carrinho de compras"""
        try:
            if self.carrinho:
                reply = QMessageBox.question(self, "Limpar Carrinho", 
                                           "Tem certeza que deseja limpar o carrinho?",
                                           QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    self.carrinho.clear()
                    self.atualizar_carrinho()
                    self.valor_pago_input.clear()
                    self.cliente_input.clear()
                    QMessageBox.information(self, "Sucesso", "Carrinho limpo com sucesso!")
            else:
                QMessageBox.information(self, "Info", "O carrinho já está vazio.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao limpar carrinho: {str(e)}")
    
        # No método finalizar_venda, substituir a parte de pagamento:
    def finalizar_venda(self):
        """Finaliza a venda e salva na base de dados - Com múltiplos pagamentos"""
        try:
            if not self.carrinho:
                QMessageBox.warning(self, "Carrinho Vazio", "Adicione produtos ao carrinho antes de finalizar a venda.")
                return
            
            # Validar usuário
            if self.usuario_atual is None:
                QMessageBox.critical(self, "Erro de Sessão", "Sessão inválida. Faça login novamente.")
                self.logout_requested.emit()
                return
            
            total_text = self.lbl_total.text().split(": ")[1].replace(" Kz", "").replace(',', '.').strip()
            total_geral = Decimal(total_text)
            
            # Processar cliente se fornecido
            cliente_id = None
            codigo_cartao = self.cliente_input.text().strip()
            if codigo_cartao:
                cliente = self.cliente_model.obter_por_codigo_cartao(codigo_cartao)
                if cliente:
                    cliente_id = cliente['id']
                    cliente_nome = cliente['nome']
                else:
                    QMessageBox.warning(self, "Cliente Não Encontrado", "Cartão cliente não encontrado!")
                    return
            else:
                cliente_nome = "Não registado"
            
            # Abrir diálogo de múltiplos pagamentos
            dialog = DialogMultiplosPagamentos(self.db, total_geral, self)
            if dialog.exec_() == QDialog.Accepted:
                pagamentos = dialog.get_pagamentos()
                
                if not pagamentos:
                    QMessageBox.warning(self, "Erro", "Nenhum pagamento foi adicionado.")
                    return
                
                # Confirmar venda
                confirm_text = (
                    f"🎯 CONFIRMAR VENDA\n\n"
                    f"📦 Itens: {len(self.carrinho)}\n"
                    f"💳 Total: {total_geral:.2f} Kz\n"
                    f"👤 Cliente: {cliente_nome}\n"
                    f"💵 Pagamentos: {len(pagamentos)} forma(s)\n"
                )
                
                for i, pagamento in enumerate(pagamentos, 1):
                    confirm_text += f"  {i}. {pagamento['forma_pagamento_nome']}: {pagamento['valor']:.2f} Kz\n"
                    if pagamento.get('troco', 0) > 0:
                        confirm_text += f"     Troco: {pagamento['troco']:.2f} Kz\n"
                
                troco_total = sum(p.get('troco', 0) for p in pagamentos)
                if troco_total > 0:
                    confirm_text += f"\n🔄 Troco Total: {troco_total:.2f} Kz"
                
                reply = QMessageBox.question(self, "Confirmar Venda", confirm_text,
                                           QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    self.salvar_venda(cliente_id, pagamentos, total_geral)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def salvar_venda(self, cliente_id, pagamentos, total_geral):
        """Salva a venda com múltiplos pagamentos e gera recibo"""
        try:
            print("💾 SALVANDO VENDA COM MÚLTIPLOS PAGAMENTOS")
            print("=" * 50)
            
            # 1. Preparar dados da venda
            subtotal_sem_iva = Decimal(self.lbl_subtotal.text().split(": ")[1].replace(" Kz", "").replace(',', '.'))
            total_iva = Decimal(self.lbl_iva.text().split(": ")[1].replace(" Kz", "").replace(',', '.'))
            
            # Obter empresa e caixa
            empresa = self.db.execute_query("SELECT id FROM empresas LIMIT 1")[0]
            caixa = self.db.execute_query("SELECT id FROM caixas WHERE ativo = 1 LIMIT 1")[0]
            
            dados_venda = {
                'empresa_id': empresa['id'],
                'caixa_id': caixa['id'],
                'usuario_id': self.usuario_atual['id'],
                'cliente_id': cliente_id,
                'total_sem_iva': float(subtotal_sem_iva),
                'total_iva': float(total_iva),
                'total_com_iva': float(total_geral)
            }
            
            # 2. Preparar itens
            itens_venda = []
            for item in self.carrinho:
                subtotal_item_sem_iva = item['preco_venda'] * item['quantidade']
                iva_item = Calculos.calcular_iva(subtotal_item_sem_iva, item['taxa_iva'])
                
                item_data = {
                    'produto_id': int(item['id']),
                    'quantidade': int(item['quantidade']),
                    'preco_unitario': float(item['preco_venda']),
                    'taxa_iva_id': int(item['taxa_iva_id']),
                    'valor_iva': float(iva_item),
                    'subtotal': float(subtotal_item_sem_iva + iva_item),
                    'desconto': 0.0
                }
                itens_venda.append(item_data)
            
            # 3. Processar venda completa
            sucesso, resultado = self.venda_model.processar_venda_completa(
                dados_venda, itens_venda, pagamentos
            )
            
            if sucesso:
                # 4. Gerar recibo
                self.gerar_recibo_automatico(resultado)
                
                QMessageBox.information(self, "✅ Venda Concluída", 
                                      f"Venda finalizada com sucesso!\n\n"
                                      f"📋 Número: {resultado}\n"
                                      f"💳 Total: {total_geral:.2f} Kz\n"
                                      f"📦 Itens: {len(self.carrinho)}\n"
                                      f"💵 Pagamentos: {len(pagamentos)} forma(s)")
                
                # 5. Limpar interface
                self.carrinho.clear()
                self.atualizar_carrinho()
                self.valor_pago_input.clear()
                self.cliente_input.clear()
                self.carregar_produtos_reais()
                
            else:
                QMessageBox.critical(self, "❌ Erro na Venda", 
                                   f"Erro ao processar venda:\n{resultado}")
                
        except Exception as e:
            error_msg = f"Erro crítico ao salvar venda:\n{str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "❌ Erro Crítico", error_msg)
    
    def gerar_recibo_automatico(self, numero_venda):
        """Gera recibo automaticamente após venda"""
        try:
            # Obter dados completos da venda
            detalhes_venda = self.venda_model.obter_detalhes_venda_por_numero(numero_venda)
            
            if not detalhes_venda:
                print("⚠️ Não foi possível obter detalhes da venda para gerar recibo")
                return
            
            venda = detalhes_venda['venda']
            itens = detalhes_venda['itens']
            pagamentos = detalhes_venda['pagamentos']
            
            # Obter informações da empresa
            empresa_info = self.db.execute_query(
                "SELECT nome, nif, telefone, endereco FROM empresas WHERE id = %s", 
                (venda['empresa_id'],)
            )[0]
            
            # Gerador de recibos
            gerador = GeradorRecibos(self.config)
            
            # Gerar recibo PDF
            recibo_pdf = gerador.gerar_recibo_venda(venda, itens, pagamentos, empresa_info)
            
            # Gerar recibo simplificado (para impressão)
            recibo_simple = gerador.gerar_recibo_simplificado(venda, itens, pagamentos)
            
            # Tentar imprimir automaticamente se configurado
            if self.config.getboolean('Impressora', 'impressao_automatica', fallback=True):
                self.imprimir_recibo_automatico(recibo_simple)
            
            print(f"✅ Recibos gerados: {recibo_pdf}, {recibo_simple}")
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar recibo automático: {e}")
    
    def imprimir_recibo_automatico(self, arquivo_recibo):
        """Imprime recibo automaticamente"""
        try:
            if self.config.getboolean('Impressora', 'impressao_automatica', fallback=True):
                from utils.impressora import Impressora
                impressora = Impressora(self.config)
                
                # Ler conteúdo do arquivo e imprimir
                with open(arquivo_recibo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                dados_impressao = {
                    'conteudo': conteudo,
                    'numero_venda': arquivo_recibo.split('_')[-1].replace('.txt', '')
                }
                
                impressora.imprimir_recibo(dados_impressao)
                print("✅ Recibo enviado para impressão automática")
                
        except Exception as e:
            print(f"⚠️ Erro na impressão automática: {e}")
                
    def filtrar_produtos(self, texto):
        """Filtra produtos baseado no texto"""
        try:
            produtos_filtrados = self.produto_model.obter_todos(texto)
            self.criar_botoes_produtos(produtos_filtrados)
        except Exception as e:
            print(f"Erro ao filtrar produtos: {e}")
    
    def carregar_dados(self):
        """Carrega dados iniciais"""
        self.carregar_produtos_reais()
        
    def closeEvent(self, event):
        """Evento chamado quando a janela é fechada"""
        if self.scanner:
            self.scanner.fechar()
        event.accept()