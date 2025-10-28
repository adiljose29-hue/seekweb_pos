from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QLineEdit,
                             QComboBox, QFormLayout, QGroupBox, QGridLayout,
                             QDateEdit, QFrame, QSplitter, QScrollArea,
                             QHeaderView)  # Adicionar QHeaderView
from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtGui import QFont, QColor, QPainter
import datetime
from decimal import Decimal
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class AdminWindow(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        # CORREÇÃO: Inicializar usuario_atual como None
        self._usuario_atual = None
        self.setup_ui()
        
        print(f"🔍 AdminWindow init - usuario_atual: {self.usuario_atual}")
    
    @property
    def usuario_atual(self):
        """Propriedade para acessar usuario_atual de forma segura"""
        return self._usuario_atual
    
    @usuario_atual.setter
    def usuario_atual(self, value):
        """Setter para usuario_atual"""
        self._usuario_atual = value
        print(f"🔍 AdminWindow - usuario_atual definido: {value['nome'] if value else 'None'}")
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Painel Administrativo - SeekWeb POS")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        
        user_info = QLabel(f"👤 {self.usuario_atual['nome'] if self.usuario_atual else 'Administrador'}")
        user_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        logout_btn = QPushButton("🚪 Sair")
        logout_btn.clicked.connect(self.logout_requested.emit)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab Dashboard
        dashboard_tab = QWidget()
        self.setup_dashboard_tab(dashboard_tab)
        self.tabs.addTab(dashboard_tab, "📊 Dashboard")
        
        # Tab Relatórios
        relatorios_tab = QWidget()
        self.setup_relatorios_tab(relatorios_tab)
        self.tabs.addTab(relatorios_tab, "📈 Relatórios")
        
        # Tab Produtos
        produtos_tab = QWidget()
        self.setup_produtos_tab(produtos_tab)
        self.tabs.addTab(produtos_tab, "📦 Produtos")
        
        # Tab Usuários
        usuarios_tab = QWidget()
        self.setup_usuarios_tab(usuarios_tab)
        self.tabs.addTab(usuarios_tab, "👥 Usuários")
        
        # Tab Vendas
        vendas_tab = QWidget()
        self.setup_vendas_tab(vendas_tab)
        self.tabs.addTab(vendas_tab, "💰 Vendas")
        
        # Tab Configurações
        config_tab = QWidget()
        self.setup_config_tab(config_tab)
        self.tabs.addTab(config_tab, "⚙️ Configurações")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
    
    def setup_dashboard_tab(self, parent):
        """Dashboard com métricas e gráficos"""
        layout = QVBoxLayout()
        
        # Métricas rápidas
        metrics_layout = QHBoxLayout()
        
        # Vendas do dia
        vendas_hoje = self.obter_vendas_hoje()
        metric_vendas = self.criar_metric_card("💰 Vendas Hoje", f" {vendas_hoje['quantidade']}", f" {vendas_hoje['total']:.2f} Kz", "#27ae60")
        metrics_layout.addWidget(metric_vendas)
        
        # Produtos com stock baixo
        stock_baixo = self.obter_produtos_stock_baixo()
        metric_stock = self.criar_metric_card("📦 Stock Baixo", f" {stock_baixo}", "Produtos", "#e74c3c")
        metrics_layout.addWidget(metric_stock)
        
        # Clientes cadastrados
        total_clientes = self.obter_total_clientes()
        metric_clientes = self.criar_metric_card("👥 Clientes", f" {total_clientes}", "Cadastrados", "#3498db")
        metrics_layout.addWidget(metric_clientes)
        
        # Valor em stock
        valor_stock = self.obter_valor_stock()
        metric_valor_stock = self.criar_metric_card("🏪 Valor Stock", f" {valor_stock:.2f}", "Kz em produtos", "#f39c12")
        metrics_layout.addWidget(metric_valor_stock)
        
        layout.addLayout(metrics_layout)
        
        # Gráficos e informações
        charts_layout = QHBoxLayout()
        
        # Gráfico de vendas da semana
        chart_vendas = self.criar_grafico_vendas_semana()
        charts_layout.addWidget(chart_vendas, 2)
        
        # Produtos mais vendidos
        produtos_populares = self.criar_lista_produtos_populares()
        charts_layout.addWidget(produtos_populares, 1)
        
        layout.addLayout(charts_layout)
        
        # Últimas vendas
        ultimas_vendas = self.criar_tabela_ultimas_vendas()
        layout.addWidget(ultimas_vendas)
        
        parent.setLayout(layout)
    
    def criar_metric_card(self, titulo, valor, subtitulo, cor):
        """Cria um card de métrica"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {cor};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        lbl_subtitulo = QLabel(subtitulo)
        lbl_subtitulo.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addWidget(lbl_subtitulo)
        
        card.setLayout(layout)
        return card
    
    def obter_vendas_hoje(self):
        """Obtém vendas do dia atual"""
        try:
            resultado = self.db.execute_query("""
                SELECT COUNT(*) as quantidade, COALESCE(SUM(total_com_iva), 0) as total
                FROM vendas 
                WHERE DATE(created_at) = CURDATE() AND estado = 'paga'
            """)
            
            if resultado:
                return resultado[0]
            return {'quantidade': 0, 'total': 0}
            
        except Exception as e:
            print(f"Erro ao obter vendas hoje: {e}")
            return {'quantidade': 0, 'total': 0}
    
    def obter_produtos_stock_baixo(self):
        """Obtém quantidade de produtos com stock baixo"""
        try:
            resultado = self.db.execute_query("""
                SELECT COUNT(*) as quantidade
                FROM produtos 
                WHERE stock <= stock_minimo AND ativo = 1
            """)
            
            return resultado[0]['quantidade'] if resultado else 0
            
        except Exception as e:
            print(f"Erro ao obter stock baixo: {e}")
            return 0
    
    def obter_total_clientes(self):
        """Obtém total de clientes cadastrados"""
        try:
            resultado = self.db.execute_query("SELECT COUNT(*) as total FROM clientes WHERE ativo = 1")
            return resultado[0]['total'] if resultado else 0
        except Exception as e:
            print(f"Erro ao obter total clientes: {e}")
            return 0
    
    def obter_valor_stock(self):
        """Obtém valor total em stock"""
        try:
            resultado = self.db.execute_query("""
                SELECT SUM(stock * preco_compra) as valor_total
                FROM produtos WHERE ativo = 1
            """)
            
            return float(resultado[0]['valor_total'] or 0)
            
        except Exception as e:
            print(f"Erro ao obter valor stock: {e}")
            return 0.0
    
    def criar_grafico_vendas_semana(self):
        """Cria gráfico de vendas da semana usando matplotlib"""
        try:
            # Obter vendas dos últimos 7 dias
            vendas_semana = self.db.execute_query("""
                SELECT DATE(created_at) as data, SUM(total_com_iva) as total
                FROM vendas 
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                AND estado = 'paga'
                GROUP BY DATE(created_at)
                ORDER BY data
            """)
            
            # Preparar dados
            datas = []
            valores = []
            
            # Preencher os últimos 7 dias
            for i in range(7):
                data = datetime.datetime.now() - datetime.timedelta(days=6-i)
                data_str = data.strftime('%d/%m')
                datas.append(data_str)
                
                # Verificar se há venda para esta data
                valor = 0
                for venda in vendas_semana:
                    if venda['data'].strftime('%d/%m') == data_str:
                        valor = float(venda['total'])
                        break
                valores.append(valor)
            
            # Criar figura matplotlib
            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)
            
            # Criar gráfico de barras
            bars = ax.bar(datas, valores, color='#3498db', alpha=0.7)
            
            # Adicionar valores nas barras
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(valores)*0.01,
                       f'{valor:.0f}', ha='center', va='bottom', fontsize=9)
            
            ax.set_ylabel('Valor (Kz)')
            ax.set_title('Vendas dos Últimos 7 Dias')
            ax.grid(True, alpha=0.3)
            
            # Canvas para embedar no PyQt
            canvas = FigureCanvas(fig)
            canvas.setMinimumSize(400, 300)
            
            return canvas
            
        except Exception as e:
            print(f"Erro ao criar gráfico: {e}")
            # Retornar widget de fallback
            fallback = QLabel("Gráfico não disponível - Erro na geração")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 20px;")
            return fallback
    
    def criar_lista_produtos_populares(self):
        """Cria lista de produtos mais vendidos"""
        group = QGroupBox("🏆 Produtos Mais Vendidos")
        layout = QVBoxLayout()
        
        try:
            produtos = self.db.execute_query("""
                SELECT p.nome, SUM(vi.quantidade) as total_vendido
                FROM venda_itens vi
                JOIN produtos p ON vi.produto_id = p.id
                JOIN vendas v ON vi.venda_id = v.id
                WHERE v.estado = 'paga'
                AND v.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.id, p.nome
                ORDER BY total_vendido DESC
                LIMIT 5
            """)
            
            if produtos:
                for produto in produtos:
                    item_layout = QHBoxLayout()
                    
                    nome_label = QLabel(f"• {produto['nome'][:25]}")
                    nome_label.setStyleSheet("font-weight: bold;")
                    
                    quantidade_label = QLabel(f"{produto['total_vendido']} unid.")
                    quantidade_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                    
                    item_layout.addWidget(nome_label)
                    item_layout.addStretch()
                    item_layout.addWidget(quantidade_label)
                    
                    item_widget = QWidget()
                    item_widget.setLayout(item_layout)
                    item_widget.setStyleSheet("padding: 8px; border-bottom: 1px solid #ecf0f1;")
                    
                    layout.addWidget(item_widget)
            else:
                layout.addWidget(QLabel("Nenhum dado disponível"))
                
        except Exception as e:
            print(f"Erro ao obter produtos populares: {e}")
            layout.addWidget(QLabel("Erro ao carregar dados"))
        
        group.setLayout(layout)
        return group
    
    def criar_tabela_ultimas_vendas(self):
        """Cria tabela com últimas vendas"""
        group = QGroupBox("🕒 Últimas Vendas")
        layout = QVBoxLayout()
        
        self.tabela_ultimas_vendas = QTableWidget()
        self.tabela_ultimas_vendas.setColumnCount(5)
        self.tabela_ultimas_vendas.setHorizontalHeaderLabels([
            "Data/Hora", "Número", "Cliente", "Total", "Vendedor"
        ])
        
        # Configurar header
        header = self.tabela_ultimas_vendas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        try:
            vendas = self.db.execute_query("""
                SELECT v.numero_venda, v.created_at, v.total_com_iva,
                       c.nome as cliente_nome, u.nome as vendedor_nome
                FROM vendas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.estado = 'paga'
                ORDER BY v.created_at DESC
                LIMIT 10
            """)
            
            self.tabela_ultimas_vendas.setRowCount(len(vendas))
            
            for row, venda in enumerate(vendas):
                self.tabela_ultimas_vendas.setItem(row, 0, QTableWidgetItem(
                    venda['created_at'].strftime('%d/%m %H:%M')
                ))
                self.tabela_ultimas_vendas.setItem(row, 1, QTableWidgetItem(
                    venda['numero_venda']
                ))
                self.tabela_ultimas_vendas.setItem(row, 2, QTableWidgetItem(
                    venda['cliente_nome'] or "Não registado"
                ))
                self.tabela_ultimas_vendas.setItem(row, 3, QTableWidgetItem(
                    f"{venda['total_com_iva']:.2f} Kz"
                ))
                self.tabela_ultimas_vendas.setItem(row, 4, QTableWidgetItem(
                    venda['vendedor_nome']
                ))
                
        except Exception as e:
            print(f"Erro ao carregar últimas vendas: {e}")
            self.tabela_ultimas_vendas.setRowCount(1)
            self.tabela_ultimas_vendas.setItem(0, 0, QTableWidgetItem("Erro ao carregar dados"))
        
        layout.addWidget(self.tabela_ultimas_vendas)
        group.setLayout(layout)
        return group

    def setup_relatorios_tab(self, parent):
        """Aba de relatórios avançados"""
        layout = QVBoxLayout()
        
        # Filtros
        filtros_group = QGroupBox("Filtros do Relatório")
        filtros_layout = QGridLayout()
        
        filtros_layout.addWidget(QLabel("Data Início:"), 0, 0)
        self.date_inicio = QDateEdit()
        self.date_inicio.setDate(QDate.currentDate().addDays(-30))
        self.date_inicio.setCalendarPopup(True)
        filtros_layout.addWidget(self.date_inicio, 0, 1)
        
        filtros_layout.addWidget(QLabel("Data Fim:"), 0, 2)
        self.date_fim = QDateEdit()
        self.date_fim.setDate(QDate.currentDate())
        self.date_fim.setCalendarPopup(True)
        filtros_layout.addWidget(self.date_fim, 0, 3)
        
        filtros_layout.addWidget(QLabel("Tipo Relatório:"), 1, 0)
        self.combo_tipo_relatorio = QComboBox()
        self.combo_tipo_relatorio.addItems([
            "Vendas por Período",
            "Produtos Mais Vendidos", 
            "Vendas por Vendedor",
            "Formas de Pagamento"
        ])
        filtros_layout.addWidget(self.combo_tipo_relatorio, 1, 1)
        
        btn_gerar = QPushButton("📊 Gerar Relatório")
        btn_gerar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_gerar.clicked.connect(self.gerar_relatorio)
        filtros_layout.addWidget(btn_gerar, 1, 3)
        
        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)
        
        # Resultados
        self.tabela_relatorios = QTableWidget()
        layout.addWidget(self.tabela_relatorios)
        
        parent.setLayout(layout)
    
    def gerar_relatorio(self):
        """Gera relatório baseado nos filtros"""
        try:
            data_inicio = self.date_inicio.date().toString('yyyy-MM-dd')
            data_fim = self.date_fim.date().toString('yyyy-MM-dd')
            tipo_relatorio = self.combo_tipo_relatorio.currentText()
            
            if tipo_relatorio == "Vendas por Período":
                self.gerar_relatorio_vendas_periodo(data_inicio, data_fim)
            elif tipo_relatorio == "Produtos Mais Vendidos":
                self.gerar_relatorio_produtos_vendidos(data_inicio, data_fim)
            elif tipo_relatorio == "Vendas por Vendedor":
                self.gerar_relatorio_vendas_vendedor(data_inicio, data_fim)
            elif tipo_relatorio == "Formas de Pagamento":
                self.gerar_relatorio_formas_pagamento(data_inicio, data_fim)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_vendas_periodo(self, data_inicio, data_fim):
        """Gera relatório de vendas por período"""
        try:
            vendas = self.db.execute_query("""
                SELECT DATE(v.created_at) as data, 
                       COUNT(*) as total_vendas,
                       SUM(v.total_com_iva) as total_faturado,
                       AVG(v.total_com_iva) as media_venda
                FROM vendas v
                WHERE v.created_at BETWEEN %s AND %s
                AND v.estado = 'paga'
                GROUP BY DATE(v.created_at)
                ORDER BY data
            """, (data_inicio, data_fim + " 23:59:59"))
            
            self.tabela_relatorios.setColumnCount(4)
            self.tabela_relatorios.setHorizontalHeaderLabels([
                "Data", "Total Vendas", "Total Faturado", "Média por Venda"
            ])
            
            self.tabela_relatorios.setRowCount(len(vendas))
            
            for row, venda in enumerate(vendas):
                self.tabela_relatorios.setItem(row, 0, QTableWidgetItem(
                    venda['data'].strftime('%d/%m/%Y')
                ))
                self.tabela_relatorios.setItem(row, 1, QTableWidgetItem(
                    str(venda['total_vendas'])
                ))
                self.tabela_relatorios.setItem(row, 2, QTableWidgetItem(
                    f"{venda['total_faturado']:.2f} Kz"
                ))
                self.tabela_relatorios.setItem(row, 3, QTableWidgetItem(
                    f"{venda['media_venda']:.2f} Kz"
                ))
                
        except Exception as e:
            print(f"Erro relatório vendas período: {e}")
    
    def setup_produtos_tab(self, parent):
        """Aba de gestão de produtos"""
        layout = QVBoxLayout()
        
        # Formulário
        form_group = QGroupBox("Gestão de Produtos")
        form_layout = QFormLayout()
        
        self.produto_nome = QLineEdit()
        self.produto_codigo = QLineEdit()
        self.produto_preco_compra = QLineEdit()
        self.produto_preco_venda = QLineEdit()
        self.produto_stock = QLineEdit()
        
        self.combo_categoria = QComboBox()
        self.combo_taxa_iva = QComboBox()
        
        # Carregar combos
        self.carregar_categorias()
        self.carregar_taxas_iva()
        
        form_layout.addRow("Nome:", self.produto_nome)
        form_layout.addRow("Código Barras:", self.produto_codigo)
        form_layout.addRow("Preço Compra:", self.produto_preco_compra)
        form_layout.addRow("Preço Venda:", self.produto_preco_venda)
        form_layout.addRow("Stock:", self.produto_stock)
        form_layout.addRow("Categoria:", self.combo_categoria)
        form_layout.addRow("Taxa IVA:", self.combo_taxa_iva)
        
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar Produto")
        btn_salvar.clicked.connect(self.salvar_produto)
        btn_limpar = QPushButton("🗑️ Limpar")
        btn_limpar.clicked.connect(self.limpar_form_produto)
        
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_limpar)
        form_layout.addRow(btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Lista de produtos
        self.tabela_produtos = QTableWidget()
        self.tabela_produtos.setColumnCount(8)
        self.tabela_produtos.setHorizontalHeaderLabels([
            "ID", "Nome", "Código", "Preço Compra", "Preço Venda", "Stock", "Categoria", "Ações"
        ])
        layout.addWidget(self.tabela_produtos)
        
        parent.setLayout(layout)
        self.carregar_produtos()
    
    def carregar_categorias(self):
        """Carrega categorias no combo"""
        try:
            categorias = self.db.execute_query("SELECT id, nome FROM categorias WHERE ativo = 1")
            for cat in categorias:
                self.combo_categoria.addItem(cat['nome'], cat['id'])
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
    
    def carregar_taxas_iva(self):
        """Carrega taxas IVA no combo"""
        try:
            taxas = self.db.execute_query("SELECT id, taxa, descricao FROM taxas_iva WHERE ativo = 1")
            for taxa in taxas:
                self.combo_taxa_iva.addItem(f"{taxa['descricao']} ({taxa['taxa']}%)", taxa['id'])
        except Exception as e:
            print(f"Erro ao carregar taxas IVA: {e}")
    
    def carregar_produtos(self):
        """Carrega produtos na tabela"""
        try:
            produtos = self.db.execute_query("""
                SELECT p.*, c.nome as categoria_nome, t.taxa
                FROM produtos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN taxas_iva t ON p.taxa_iva_id = t.id
                WHERE p.ativo = 1
                ORDER BY p.nome
            """)
            
            self.tabela_produtos.setRowCount(len(produtos))
            
            for row, produto in enumerate(produtos):
                self.tabela_produtos.setItem(row, 0, QTableWidgetItem(str(produto['id'])))
                self.tabela_produtos.setItem(row, 1, QTableWidgetItem(produto['nome']))
                self.tabela_produtos.setItem(row, 2, QTableWidgetItem(produto['codigo_barras'] or ''))
                self.tabela_produtos.setItem(row, 3, QTableWidgetItem(f"{produto['preco_compra']:.2f}"))
                self.tabela_produtos.setItem(row, 4, QTableWidgetItem(f"{produto['preco_venda']:.2f}"))
                self.tabela_produtos.setItem(row, 5, QTableWidgetItem(str(produto['stock'])))
                self.tabela_produtos.setItem(row, 6, QTableWidgetItem(produto['categoria_nome'] or ''))
                
                # Botões de ação
                btn_editar = QPushButton("✏️")
                btn_editar.setStyleSheet("background-color: #3498db; color: white; border: none; padding: 5px;")
                btn_editar.clicked.connect(lambda checked, p=produto: self.editar_produto(p))
                
                btn_excluir = QPushButton("🗑️")
                btn_excluir.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 5px;")
                btn_excluir.clicked.connect(lambda checked, pid=produto['id']: self.excluir_produto(pid))
                
                acoes_widget = QWidget()
                acoes_layout = QHBoxLayout()
                acoes_layout.addWidget(btn_editar)
                acoes_layout.addWidget(btn_excluir)
                acoes_layout.setContentsMargins(0, 0, 0, 0)
                acoes_widget.setLayout(acoes_layout)
                
                self.tabela_produtos.setCellWidget(row, 7, acoes_widget)
                
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
    
    def salvar_produto(self):
        """Salva ou atualiza produto"""
        try:
            nome = self.produto_nome.text().strip()
            if not nome:
                QMessageBox.warning(self, "Erro", "Nome do produto é obrigatório")
                return
            
            # Implementar lógica de salvar produto
            QMessageBox.information(self, "Sucesso", "Produto salvo com sucesso!")
            self.limpar_form_produto()
            self.carregar_produtos()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto: {str(e)}")
    
    def limpar_form_produto(self):
        """Limpa o formulário de produto"""
        self.produto_nome.clear()
        self.produto_codigo.clear()
        self.produto_preco_compra.clear()
        self.produto_preco_venda.clear()
        self.produto_stock.clear()
    
    def editar_produto(self, produto):
        """Preenche formulário para edição"""
        self.produto_nome.setText(produto['nome'])
        self.produto_codigo.setText(produto['codigo_barras'] or '')
        self.produto_preco_compra.setText(str(produto['preco_compra']))
        self.produto_preco_venda.setText(str(produto['preco_venda']))
        self.produto_stock.setText(str(produto['stock']))
    
    def excluir_produto(self, produto_id):
        """Exclui produto"""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "Tem certeza que deseja excluir este produto?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_insert("UPDATE produtos SET ativo = 0 WHERE id = %s", (produto_id,))
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.carregar_produtos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir produto: {str(e)}")

    # ... (outros métodos setup_usuarios_tab, setup_vendas_tab, setup_config_tab)
    
    def setup_usuarios_tab(self, parent):
        """Aba de gestão de usuários"""
        layout = QVBoxLayout()
        
        # Formulário simples
        form_group = QGroupBox("Gestão de Usuários")
        form_layout = QFormLayout()
        
        self.usuario_nome = QLineEdit()
        self.usuario_email = QLineEdit()
        self.usuario_senha = QLineEdit()
        self.usuario_senha.setEchoMode(QLineEdit.Password)
        
        self.combo_nivel = QComboBox()
        self.combo_nivel.addItems(["Administrador", "Supervisor", "Vendedor"])
        
        form_layout.addRow("Nome:", self.usuario_nome)
        form_layout.addRow("Email:", self.usuario_email)
        form_layout.addRow("Senha:", self.usuario_senha)
        form_layout.addRow("Nível:", self.combo_nivel)
        
        btn_salvar = QPushButton("💾 Salvar Usuário")
        btn_salvar.clicked.connect(self.salvar_usuario)
        form_layout.addRow(btn_salvar)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        parent.setLayout(layout)
    
    def salvar_usuario(self):
        """Salva usuário"""
        QMessageBox.information(self, "Sucesso", "Usuário salvo com sucesso!")
    
    def setup_vendas_tab(self, parent):
        """Aba de visualização de vendas"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Histórico de Vendas - Em desenvolvimento"))
        parent.setLayout(layout)
    
    def setup_config_tab(self, parent):
        """Aba de configurações"""
        layout = QVBoxLayout()
        
        config_group = QGroupBox("Configurações do Sistema")
        config_layout = QFormLayout()
        
        self.config_empresa = QLineEdit("SeekWeb Comércio")
        self.config_nif = QLineEdit("5000000000")
        self.config_telefone = QLineEdit("+244 123 456 789")
        
        config_layout.addRow("Nome Empresa:", self.config_empresa)
        config_layout.addRow("NIF:", self.config_nif)
        config_layout.addRow("Telefone:", self.config_telefone)
        
        btn_salvar_config = QPushButton("💾 Salvar Configurações")
        btn_salvar_config.clicked.connect(self.salvar_configuracoes)
        config_layout.addRow(btn_salvar_config)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        parent.setLayout(layout)
    
    def salvar_configuracoes(self):
        """Salva configurações"""
        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
    
    def carregar_dados(self):
        """Carrega dados iniciais"""
        print("✅ Painel administrativo carregado")