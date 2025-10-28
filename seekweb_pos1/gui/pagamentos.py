from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QLineEdit, QMessageBox, QHeaderView,  # Adicionar QHeaderView
                             QGroupBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from decimal import Decimal

class DialogMultiplosPagamentos(QDialog):
    def __init__(self, db, total_venda, parent=None):
        super().__init__(parent)
        self.db = db
        self.total_venda = Decimal(str(total_venda))
        self.pagamentos = []
        self.total_pago = Decimal('0')
        self.setup_ui()
        self.carregar_formas_pagamento()
    
    def setup_ui(self):
        self.setWindowTitle("Múltiplas Formas de Pagamento")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Total da venda
        total_group = QGroupBox("Total da Venda")
        total_layout = QVBoxLayout()
        self.lbl_total = QLabel(f"Total a Pagar: {self.total_venda:.2f} Kz")
        self.lbl_total.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #2c3e50; background-color: #ecf0f1; padding: 10px; border-radius: 5px;")
        total_layout.addWidget(self.lbl_total)
        total_group.setLayout(total_layout)
        layout.addWidget(total_group)
        
        # Formulário de pagamento
        form_group = QGroupBox("Adicionar Pagamento")
        form_layout = QVBoxLayout()
        
        # Forma de pagamento
        forma_layout = QHBoxLayout()
        forma_layout.addWidget(QLabel("Forma de Pagamento:"))
        self.combo_forma_pagamento = QComboBox()
        forma_layout.addWidget(self.combo_forma_pagamento)
        form_layout.addLayout(forma_layout)
        
        # Valor
        valor_layout = QHBoxLayout()
        valor_layout.addWidget(QLabel("Valor:"))
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setMaximum(1000000.00)
        self.spin_valor.setDecimals(2)
        self.spin_valor.setSuffix(" Kz")
        self.spin_valor.setValue(float(self.total_venda - self.total_pago))
        valor_layout.addWidget(self.spin_valor)
        form_layout.addLayout(valor_layout)
        
        # Referência (para cartões, transferências)
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Referência:"))
        self.input_referencia = QLineEdit()
        self.input_referencia.setPlaceholderText("Opcional - para cartões, transferências, etc.")
        ref_layout.addWidget(self.input_referencia)
        form_layout.addLayout(ref_layout)
        
        # Botão adicionar
        self.btn_adicionar = QPushButton("➕ Adicionar Pagamento")
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_pagamento)
        form_layout.addWidget(self.btn_adicionar)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Tabela de pagamentos
        tabela_group = QGroupBox("Pagamentos Adicionados")
        tabela_layout = QVBoxLayout()
        
        self.tabela_pagamentos = QTableWidget()
        self.tabela_pagamentos.setColumnCount(4)
        self.tabela_pagamentos.setHorizontalHeaderLabels(["Forma Pagamento", "Valor", "Referência", "Ações"])
        self.tabela_pagamentos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela_layout.addWidget(self.tabela_pagamentos)
        
        tabela_group.setLayout(tabela_layout)
        layout.addWidget(tabela_group)
        
        # Resumo
        resumo_group = QGroupBox("Resumo")
        resumo_layout = QVBoxLayout()
        
        self.lbl_total_pago = QLabel(f"Total Pago: {self.total_pago:.2f} Kz")
        self.lbl_restante = QLabel(f"Restante: {(self.total_venda - self.total_pago):.2f} Kz")
        self.lbl_troco = QLabel("Troco: 0.00 Kz")
        
        for lbl in [self.lbl_total_pago, self.lbl_restante, self.lbl_troco]:
            lbl.setFont(QFont("Arial", 10, QFont.Bold))
        
        resumo_layout.addWidget(self.lbl_total_pago)
        resumo_layout.addWidget(self.lbl_restante)
        resumo_layout.addWidget(self.lbl_troco)
        
        resumo_group.setLayout(resumo_layout)
        layout.addWidget(resumo_group)
        
        # Botões de ação
        botoes_layout = QHBoxLayout()
        
        self.btn_finalizar = QPushButton("✅ Finalizar Venda")
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_finalizar.clicked.connect(self.finalizar)
        self.btn_finalizar.setEnabled(False)
        
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setStyleSheet("""
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
        self.btn_cancelar.clicked.connect(self.reject)
        
        botoes_layout.addWidget(self.btn_finalizar)
        botoes_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(botoes_layout)
        self.setLayout(layout)
        
        self.atualizar_resumo()
    
    def carregar_formas_pagamento(self):
        """Carrega formas de pagamento no ComboBox"""
        try:
            formas_pagamento = self.db.execute_query(
                "SELECT id, nome, codigo, aceita_troco FROM formas_pagamento WHERE ativo = 1 ORDER BY id"
            )
            
            for fp in formas_pagamento:
                fp_data = {
                    'id': fp['id'],
                    'nome': fp['nome'],
                    'codigo': fp['codigo'],
                    'aceita_troco': bool(fp.get('aceita_troco', False))
                }
                self.combo_forma_pagamento.addItem(fp_data['nome'], fp_data)
                
        except Exception as e:
            print(f"Erro ao carregar formas de pagamento: {e}")
    
    def adicionar_pagamento(self):
        """Adiciona um novo pagamento à lista"""
        try:
            forma_pagamento_data = self.combo_forma_pagamento.currentData()
            valor = Decimal(str(self.spin_valor.value()))
            referencia = self.input_referencia.text().strip()
            
            if not forma_pagamento_data:
                QMessageBox.warning(self, "Erro", "Selecione uma forma de pagamento.")
                return
            
            if valor <= 0:
                QMessageBox.warning(self, "Erro", "O valor deve ser maior que zero.")
                return
            
            # Verificar se o valor excede o restante
            restante = self.total_venda - self.total_pago
            if valor > restante and forma_pagamento_data['codigo'] != 'DINHEIRO':
                QMessageBox.warning(self, "Erro", 
                                  f"Valor excede o restante a pagar!\n"
                                  f"Restante: {restante:.2f} Kz\n"
                                  f"Valor: {valor:.2f} Kz")
                return
            
            pagamento = {
                'forma_pagamento_id': forma_pagamento_data['id'],
                'forma_pagamento_nome': forma_pagamento_data['nome'],
                'forma_pagamento_codigo': forma_pagamento_data['codigo'],
                'valor': float(valor),
                'referencia': referencia,
                'troco': 0.0
            }
            
            # Calcular troco se for dinheiro e valor for maior que restante
            if forma_pagamento_data['codigo'] == 'DINHEIRO' and valor > restante:
                troco = valor - restante
                pagamento['troco'] = float(troco)
                pagamento['valor'] = float(restante)  # Ajustar valor para o exato
            
            self.pagamentos.append(pagamento)
            self.atualizar_tabela_pagamentos()
            self.atualizar_resumo()
            self.limpar_formulario()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar pagamento: {str(e)}")
    
    def atualizar_tabela_pagamentos(self):
        """Atualiza a tabela de pagamentos"""
        self.tabela_pagamentos.setRowCount(len(self.pagamentos))
        
        for row, pagamento in enumerate(self.pagamentos):
            self.tabela_pagamentos.setItem(row, 0, QTableWidgetItem(pagamento['forma_pagamento_nome']))
            self.tabela_pagamentos.setItem(row, 1, QTableWidgetItem(f"{pagamento['valor']:.2f} Kz"))
            self.tabela_pagamentos.setItem(row, 2, QTableWidgetItem(pagamento['referencia']))
            
            # Botão remover
            btn_remover = QPushButton("🗑️")
            btn_remover.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_remover.clicked.connect(lambda checked, r=row: self.remover_pagamento(r))
            self.tabela_pagamentos.setCellWidget(row, 3, btn_remover)
    
    def remover_pagamento(self, index):
        """Remove um pagamento da lista"""
        if 0 <= index < len(self.pagamentos):
            self.pagamentos.pop(index)
            self.atualizar_tabela_pagamentos()
            self.atualizar_resumo()
    
    def atualizar_resumo(self):
        """Atualiza o resumo dos pagamentos"""
        self.total_pago = sum(Decimal(str(p['valor'])) for p in self.pagamentos)
        restante = self.total_venda - self.total_pago
        
        # Calcular troco total
        troco_total = sum(Decimal(str(p.get('troco', 0))) for p in self.pagamentos)
        
        self.lbl_total_pago.setText(f"Total Pago: {self.total_pago:.2f} Kz")
        self.lbl_restante.setText(f"Restante: {restante:.2f} Kz")
        self.lbl_troco.setText(f"Troco: {troco_total:.2f} Kz")
        
        # Atualizar valor sugerido no spin
        self.spin_valor.setValue(float(restante))
        
        # Habilitar/desabilitar botão finalizar
        self.btn_finalizar.setEnabled(self.total_pago >= self.total_venda)
        
        # Cor do restante
        if restante > 0:
            self.lbl_restante.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.lbl_restante.setStyleSheet("color: #27ae60; font-weight: bold;")
    
    def limpar_formulario(self):
        """Limpa o formulário após adicionar pagamento"""
        self.input_referencia.clear()
    
    def finalizar(self):
        """Finaliza o processo de múltiplos pagamentos"""
        if self.total_pago >= self.total_venda:
            self.accept()
        else:
            QMessageBox.warning(self, "Pagamento Insuficiente", 
                              f"O total pago ({self.total_pago:.2f} Kz) é menor que o total da venda ({self.total_venda:.2f} Kz).")
    
    def get_pagamentos(self):
        """Retorna a lista de pagamentos"""
        return self.pagamentos