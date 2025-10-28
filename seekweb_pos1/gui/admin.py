from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QLineEdit,
                             QComboBox, QFormLayout, QGroupBox, QGridLayout,
                             QDateEdit, QFrame, QSplitter, QScrollArea,
                             QHeaderView, QTextEdit, QDoubleSpinBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtGui import QFont, QColor, QPainter
import datetime
from decimal import Decimal
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QInputDialog, QListWidget, QListWidgetItem
import json

class AdminWindow(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._usuario_atual = None
        self.setup_ui()
    
    @property
    def usuario_atual(self):
        return self._usuario_atual

    @usuario_atual.setter
    def usuario_atual(self, value):
        self._usuario_atual = value
    
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
        
        # Tab Clientes
        clientes_tab = QWidget()
        self.setup_clientes_tab(clientes_tab)
        self.tabs.addTab(clientes_tab, "👥 Clientes")
        
        # Tab Vendas
        vendas_tab = QWidget()
        self.setup_vendas_tab(vendas_tab)
        self.tabs.addTab(vendas_tab, "💰 Vendas")
        
        # Tab Caixa
        caixa_tab = QWidget()
        self.setup_caixa_tab(caixa_tab)
        self.tabs.addTab(caixa_tab, "💵 Caixa")
        
        # Tab Promoções
        promocoes_tab = QWidget()
        self.setup_promocoes_tab(promocoes_tab)
        self.tabs.addTab(promocoes_tab, "🎯 Promoções")
        
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
            "Formas de Pagamento",
            "Clientes Mais Frequentes"
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
        
        btn_exportar = QPushButton("📤 Exportar PDF")
        btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_exportar.clicked.connect(self.exportar_relatorio)
        filtros_layout.addWidget(btn_exportar, 1, 4)
        
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
            elif tipo_relatorio == "Clientes Mais Frequentes":
                self.gerar_relatorio_clientes_frequentes(data_inicio, data_fim)
                
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
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_produtos_vendidos(self, data_inicio, data_fim):
        """Gera relatório de produtos mais vendidos"""
        try:
            produtos = self.db.execute_query("""
                SELECT p.nome, p.codigo_barras,
                       SUM(vi.quantidade) as total_vendido,
                       SUM(vi.subtotal) as total_faturado,
                       AVG(vi.preco_unitario) as preco_medio
                FROM venda_itens vi
                JOIN produtos p ON vi.produto_id = p.id
                JOIN vendas v ON vi.venda_id = v.id
                WHERE v.created_at BETWEEN %s AND %s
                AND v.estado = 'paga'
                GROUP BY p.id, p.nome, p.codigo_barras
                ORDER BY total_vendido DESC
            """, (data_inicio, data_fim + " 23:59:59"))
            
            self.tabela_relatorios.setColumnCount(5)
            self.tabela_relatorios.setHorizontalHeaderLabels([
                "Produto", "Código", "Quantidade Vendida", "Total Faturado", "Preço Médio"
            ])
            
            self.tabela_relatorios.setRowCount(len(produtos))
            
            for row, produto in enumerate(produtos):
                self.tabela_relatorios.setItem(row, 0, QTableWidgetItem(produto['nome']))
                self.tabela_relatorios.setItem(row, 1, QTableWidgetItem(produto['codigo_barras'] or ''))
                self.tabela_relatorios.setItem(row, 2, QTableWidgetItem(str(produto['total_vendido'])))
                self.tabela_relatorios.setItem(row, 3, QTableWidgetItem(f"{produto['total_faturado']:.2f} Kz"))
                self.tabela_relatorios.setItem(row, 4, QTableWidgetItem(f"{produto['preco_medio']:.2f} Kz"))
                
        except Exception as e:
            print(f"Erro relatório produtos vendidos: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_vendas_vendedor(self, data_inicio, data_fim):
        """Gera relatório de vendas por vendedor"""
        try:
            vendedores = self.db.execute_query("""
                SELECT u.nome as vendedor,
                       COUNT(*) as total_vendas,
                       SUM(v.total_com_iva) as total_faturado,
                       AVG(v.total_com_iva) as media_venda,
                       MAX(v.total_com_iva) as maior_venda
                FROM vendas v
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.created_at BETWEEN %s AND %s
                AND v.estado = 'paga'
                GROUP BY u.id, u.nome
                ORDER BY total_faturado DESC
            """, (data_inicio, data_fim + " 23:59:59"))
            
            self.tabela_relatorios.setColumnCount(5)
            self.tabela_relatorios.setHorizontalHeaderLabels([
                "Vendedor", "Total Vendas", "Total Faturado", "Média por Venda", "Maior Venda"
            ])
            
            self.tabela_relatorios.setRowCount(len(vendedores))
            
            for row, vendedor in enumerate(vendedores):
                self.tabela_relatorios.setItem(row, 0, QTableWidgetItem(vendedor['vendedor']))
                self.tabela_relatorios.setItem(row, 1, QTableWidgetItem(str(vendedor['total_vendas'])))
                self.tabela_relatorios.setItem(row, 2, QTableWidgetItem(f"{vendedor['total_faturado']:.2f} Kz"))
                self.tabela_relatorios.setItem(row, 3, QTableWidgetItem(f"{vendedor['media_venda']:.2f} Kz"))
                self.tabela_relatorios.setItem(row, 4, QTableWidgetItem(f"{vendedor['maior_venda']:.2f} Kz"))
                
        except Exception as e:
            print(f"Erro relatório vendas vendedor: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_formas_pagamento(self, data_inicio, data_fim):
        """Gera relatório de formas de pagamento"""
        try:
            formas_pagamento = self.db.execute_query("""
                SELECT fp.nome as forma_pagamento,
                       COUNT(*) as total_utilizacoes,
                       SUM(vp.valor) as total_valor,
                       (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM venda_pagamentos vp2 
                                         JOIN vendas v2 ON vp2.venda_id = v2.id 
                                         WHERE v2.created_at BETWEEN %s AND %s 
                                         AND v2.estado = 'paga')) as percentagem
                FROM venda_pagamentos vp
                JOIN formas_pagamento fp ON vp.forma_pagamento_id = fp.id
                JOIN vendas v ON vp.venda_id = v.id
                WHERE v.created_at BETWEEN %s AND %s
                AND v.estado = 'paga'
                GROUP BY fp.id, fp.nome
                ORDER BY total_valor DESC
            """, (data_inicio, data_fim + " 23:59:59", data_inicio, data_fim + " 23:59:59"))
            
            self.tabela_relatorios.setColumnCount(4)
            self.tabela_relatorios.setHorizontalHeaderLabels([
                "Forma Pagamento", "Utilizações", "Total Valor", "Percentagem"
            ])
            
            self.tabela_relatorios.setRowCount(len(formas_pagamento))
            
            for row, forma in enumerate(formas_pagamento):
                self.tabela_relatorios.setItem(row, 0, QTableWidgetItem(forma['forma_pagamento']))
                self.tabela_relatorios.setItem(row, 1, QTableWidgetItem(str(forma['total_utilizacoes'])))
                self.tabela_relatorios.setItem(row, 2, QTableWidgetItem(f"{forma['total_valor']:.2f} Kz"))
                self.tabela_relatorios.setItem(row, 3, QTableWidgetItem(f"{forma['percentagem']:.1f}%"))
                
        except Exception as e:
            print(f"Erro relatório formas pagamento: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_clientes_frequentes(self, data_inicio, data_fim):
        """Gera relatório de clientes mais frequentes"""
        try:
            clientes = self.db.execute_query("""
                SELECT c.nome, c.telefone, c.email,
                       COUNT(*) as total_compras,
                       SUM(v.total_com_iva) as total_gasto,
                       AVG(v.total_com_iva) as media_compra,
                       MAX(v.created_at) as ultima_compra
                FROM vendas v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.created_at BETWEEN %s AND %s
                AND v.estado = 'paga'
                GROUP BY c.id, c.nome, c.telefone, c.email
                ORDER BY total_gasto DESC
                LIMIT 20
            """, (data_inicio, data_fim + " 23:59:59"))
            
            self.tabela_relatorios.setColumnCount(6)
            self.tabela_relatorios.setHorizontalHeaderLabels([
                "Cliente", "Telefone", "Email", "Total Compras", "Total Gasto", "Última Compra"
            ])
            
            self.tabela_relatorios.setRowCount(len(clientes))
            
            for row, cliente in enumerate(clientes):
                self.tabela_relatorios.setItem(row, 0, QTableWidgetItem(cliente['nome']))
                self.tabela_relatorios.setItem(row, 1, QTableWidgetItem(cliente['telefone'] or ''))
                self.tabela_relatorios.setItem(row, 2, QTableWidgetItem(cliente['email'] or ''))
                self.tabela_relatorios.setItem(row, 3, QTableWidgetItem(str(cliente['total_compras'])))
                self.tabela_relatorios.setItem(row, 4, QTableWidgetItem(f"{cliente['total_gasto']:.2f} Kz"))
                self.tabela_relatorios.setItem(row, 5, QTableWidgetItem(
                    cliente['ultima_compra'].strftime('%d/%m/%Y') if cliente['ultima_compra'] else ''
                ))
                
        except Exception as e:
            print(f"Erro relatório clientes frequentes: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def exportar_relatorio(self):
        """Exporta relatório para PDF"""
        QMessageBox.information(self, "Exportar", "Funcionalidade de exportação em desenvolvimento")
    
    # CONTINUA... (Vou enviar o resto em outra mensagem devido ao limite de caracteres)
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
    def setup_vendas_tab(self, parent):
        """Aba de visualização de vendas"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Histórico de Vendas - Em desenvolvimento"))
        parent.setLayout(layout)
    
    def carregar_dados(self):
        """Carrega dados iniciais"""
        print("✅ Painel administrativo carregado")
    # ... (outros métodos setup_usuarios_tab, setup_vendas_tab, setup_config_tab)
    # ... (outros métodos Usuarios)
    def setup_usuarios_tab(self, parent):
        """Aba de gestão de usuários completa"""
        layout = QVBoxLayout()
        
        # Formulário
        form_group = QGroupBox("Adicionar/Editar Usuário")
        form_layout = QFormLayout()
        
        self.usuario_id = None  # Para controle de edição
        
        self.usuario_nome = QLineEdit()
        self.usuario_email = QLineEdit()
        self.usuario_senha = QLineEdit()
        self.usuario_senha.setEchoMode(QLineEdit.Password)
        self.usuario_codigo_barras = QLineEdit()
        
        self.combo_nivel = QComboBox()
        self.carregar_niveis_usuario()
        
        form_layout.addRow("Nome:*", self.usuario_nome)
        form_layout.addRow("Email:*", self.usuario_email)
        form_layout.addRow("Senha:*", self.usuario_senha)
        form_layout.addRow("Código Barras:", self.usuario_codigo_barras)
        form_layout.addRow("Nível:*", self.combo_nivel)
        
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar Usuário")
        btn_salvar.clicked.connect(self.salvar_usuario)
        btn_limpar = QPushButton("🗑️ Limpar")
        btn_limpar.clicked.connect(self.limpar_form_usuario)
        
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_limpar)
        form_layout.addRow(btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Lista de usuários
        self.tabela_usuarios = QTableWidget()
        self.tabela_usuarios.setColumnCount(6)
        self.tabela_usuarios.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Nível", "Estado", "Ações"
        ])
        layout.addWidget(self.tabela_usuarios)
        
        parent.setLayout(layout)
        self.carregar_usuarios()
    
    def carregar_niveis_usuario(self):
        """Carrega níveis de usuário no combo"""
        try:
            niveis = self.db.execute_query("SELECT id, nome FROM niveis_usuario ORDER BY id")
            for nivel in niveis:
                self.combo_nivel.addItem(nivel['nome'], nivel['id'])
        except Exception as e:
            print(f"Erro ao carregar níveis: {e}")
    
    def carregar_usuarios(self):
        """Carrega usuários na tabela"""
        try:
            usuarios = self.db.execute_query("""
                SELECT u.*, n.nome as nivel_nome 
                FROM usuarios u 
                JOIN niveis_usuario n ON u.nivel_id = n.id 
                WHERE u.ativo = 1
                ORDER BY u.nome
            """)
            
            self.tabela_usuarios.setRowCount(len(usuarios))
            
            for row, usuario in enumerate(usuarios):
                self.tabela_usuarios.setItem(row, 0, QTableWidgetItem(str(usuario['id'])))
                self.tabela_usuarios.setItem(row, 1, QTableWidgetItem(usuario['nome']))
                self.tabela_usuarios.setItem(row, 2, QTableWidgetItem(usuario['email']))
                self.tabela_usuarios.setItem(row, 3, QTableWidgetItem(usuario['nivel_nome']))
                self.tabela_usuarios.setItem(row, 4, QTableWidgetItem("Ativo" if usuario['ativo'] else "Inativo"))
                
                # Botões de ação
                btn_editar = QPushButton("✏️")
                btn_editar.setStyleSheet("background-color: #3498db; color: white; border: none; padding: 5px;")
                btn_editar.clicked.connect(lambda checked, u=usuario: self.editar_usuario(u))
                
                btn_excluir = QPushButton("🗑️")
                btn_excluir.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 5px;")
                btn_excluir.clicked.connect(lambda checked, uid=usuario['id']: self.excluir_usuario(uid))
                
                acoes_widget = QWidget()
                acoes_layout = QHBoxLayout()
                acoes_layout.addWidget(btn_editar)
                acoes_layout.addWidget(btn_excluir)
                acoes_layout.setContentsMargins(0, 0, 0, 0)
                acoes_widget.setLayout(acoes_layout)
                
                self.tabela_usuarios.setCellWidget(row, 5, acoes_widget)
                
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
    
    def salvar_usuario(self):
        """Salva ou atualiza usuário"""
        try:
            nome = self.usuario_nome.text().strip()
            email = self.usuario_email.text().strip()
            senha = self.usuario_senha.text().strip()
            codigo_barras = self.usuario_codigo_barras.text().strip()
            nivel_id = self.combo_nivel.currentData()
            
            if not nome or not email or not senha:
                QMessageBox.warning(self, "Erro", "Nome, email e senha são obrigatórios!")
                return
            
            if self.usuario_id:  # Edição
                if senha:  # Se senha foi alterada
                    query = """
                    UPDATE usuarios 
                    SET nome = %s, email = %s, senha = %s, codigo_barras = %s, nivel_id = %s 
                    WHERE id = %s
                    """
                    params = (nome, email, senha, codigo_barras, nivel_id, self.usuario_id)
                else:  # Manter senha atual
                    query = """
                    UPDATE usuarios 
                    SET nome = %s, email = %s, codigo_barras = %s, nivel_id = %s 
                    WHERE id = %s
                    """
                    params = (nome, email, codigo_barras, nivel_id, self.usuario_id)
            else:  # Novo usuário
                query = """
                INSERT INTO usuarios (empresa_id, nivel_id, nome, email, senha, codigo_barras, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """
                params = (1, nivel_id, nome, email, senha, codigo_barras)
            
            result = self.db.execute_insert(query, params)
            
            if result:
                QMessageBox.information(self, "Sucesso", "Usuário salvo com sucesso!")
                self.limpar_form_usuario()
                self.carregar_usuarios()
            else:
                QMessageBox.critical(self, "Erro", "Erro ao salvar usuário!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar usuário: {str(e)}")
    
    def limpar_form_usuario(self):
        """Limpa o formulário de usuário"""
        self.usuario_id = None
        self.usuario_nome.clear()
        self.usuario_email.clear()
        self.usuario_senha.clear()
        self.usuario_codigo_barras.clear()
        self.combo_nivel.setCurrentIndex(0)
    
    def editar_usuario(self, usuario):
        """Preenche formulário para edição"""
        self.usuario_id = usuario['id']
        self.usuario_nome.setText(usuario['nome'])
        self.usuario_email.setText(usuario['email'])
        self.usuario_senha.clear()  # Não mostrar senha por segurança
        self.usuario_senha.setPlaceholderText("Deixe em branco para manter atual")
        self.usuario_codigo_barras.setText(usuario['codigo_barras'] or '')
        
        # Selecionar nível correto
        index = self.combo_nivel.findData(usuario['nivel_id'])
        if index >= 0:
            self.combo_nivel.setCurrentIndex(index)
    
    def excluir_usuario(self, usuario_id):
        """Exclui usuário (desativa)"""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "Tem certeza que deseja excluir este usuário?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_insert("UPDATE usuarios SET ativo = 0 WHERE id = %s", (usuario_id,))
                QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso!")
                self.carregar_usuarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir usuário: {str(e)}")
        # ... (outros métodos Clientes)
    def setup_clientes_tab(self, parent):
        """Aba de gestão de clientes"""
        layout = QVBoxLayout()
        
        # Formulário
        form_group = QGroupBox("Adicionar/Editar Cliente")
        form_layout = QFormLayout()
        
        self.cliente_id = None
        
        self.cliente_nome = QLineEdit()
        self.cliente_telefone = QLineEdit()
        self.cliente_email = QLineEdit()
        self.cliente_nif = QLineEdit()
        self.cliente_endereco = QTextEdit()
        self.cliente_endereco.setMaximumHeight(80)
        self.cliente_codigo_cartao = QLineEdit()
        self.cliente_senha_cartao = QLineEdit()
        self.cliente_senha_cartao.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Nome:*", self.cliente_nome)
        form_layout.addRow("Telefone:", self.cliente_telefone)
        form_layout.addRow("Email:", self.cliente_email)
        form_layout.addRow("NIF:", self.cliente_nif)
        form_layout.addRow("Endereço:", self.cliente_endereco)
        form_layout.addRow("Código Cartão:", self.cliente_codigo_cartao)
        form_layout.addRow("Senha Cartão:", self.cliente_senha_cartao)
        
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar Cliente")
        btn_salvar.clicked.connect(self.salvar_cliente)
        btn_limpar = QPushButton("🗑️ Limpar")
        btn_limpar.clicked.connect(self.limpar_form_cliente)
        
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_limpar)
        form_layout.addRow(btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Lista de clientes
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(8)
        self.tabela_clientes.setHorizontalHeaderLabels([
            "ID", "Nome", "Telefone", "Email", "Cartão", "Pontos", "Estado", "Ações"
        ])
        layout.addWidget(self.tabela_clientes)
        
        parent.setLayout(layout)
        self.carregar_clientes()
    
    def carregar_clientes(self):
        """Carrega clientes na tabela"""
        try:
            clientes = self.db.execute_query("""
                SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome
            """)
            
            self.tabela_clientes.setRowCount(len(clientes))
            
            for row, cliente in enumerate(clientes):
                self.tabela_clientes.setItem(row, 0, QTableWidgetItem(str(cliente['id'])))
                self.tabela_clientes.setItem(row, 1, QTableWidgetItem(cliente['nome']))
                self.tabela_clientes.setItem(row, 2, QTableWidgetItem(cliente['telefone'] or ''))
                self.tabela_clientes.setItem(row, 3, QTableWidgetItem(cliente['email'] or ''))
                self.tabela_clientes.setItem(row, 4, QTableWidgetItem(cliente['codigo_cartao'] or ''))
                self.tabela_clientes.setItem(row, 5, QTableWidgetItem(str(cliente['pontos_fidelidade'])))
                self.tabela_clientes.setItem(row, 6, QTableWidgetItem("Ativo" if cliente['ativo'] else "Inativo"))
                
                # Botões de ação
                btn_editar = QPushButton("✏️")
                btn_editar.setStyleSheet("background-color: #3498db; color: white; border: none; padding: 5px;")
                btn_editar.clicked.connect(lambda checked, c=cliente: self.editar_cliente(c))
                
                btn_excluir = QPushButton("🗑️")
                btn_excluir.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 5px;")
                btn_excluir.clicked.connect(lambda checked, cid=cliente['id']: self.excluir_cliente(cid))
                
                acoes_widget = QWidget()
                acoes_layout = QHBoxLayout()
                acoes_layout.addWidget(btn_editar)
                acoes_layout.addWidget(btn_excluir)
                acoes_layout.setContentsMargins(0, 0, 0, 0)
                acoes_widget.setLayout(acoes_layout)
                
                self.tabela_clientes.setCellWidget(row, 7, acoes_widget)
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
    
    def salvar_cliente(self):
        """Salva ou atualiza cliente"""
        try:
            nome = self.cliente_nome.text().strip()
            telefone = self.cliente_telefone.text().strip()
            email = self.cliente_email.text().strip()
            nif = self.cliente_nif.text().strip()
            endereco = self.cliente_endereco.toPlainText().strip()
            codigo_cartao = self.cliente_codigo_cartao.text().strip()
            senha_cartao = self.cliente_senha_cartao.text().strip()
            
            if not nome:
                QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
                return
            
            if self.cliente_id:  # Edição
                if senha_cartao:  # Se senha foi alterada
                    query = """
                    UPDATE clientes 
                    SET nome = %s, telefone = %s, email = %s, nif = %s, 
                        endereco = %s, codigo_cartao = %s, senha_cartao = %s
                    WHERE id = %s
                    """
                    params = (nome, telefone, email, nif, endereco, codigo_cartao, senha_cartao, self.cliente_id)
                else:  # Manter senha atual
                    query = """
                    UPDATE clientes 
                    SET nome = %s, telefone = %s, email = %s, nif = %s, 
                        endereco = %s, codigo_cartao = %s
                    WHERE id = %s
                    """
                    params = (nome, telefone, email, nif, endereco, codigo_cartao, self.cliente_id)
            else:  # Novo cliente
                if not senha_cartao:
                    senha_cartao = "1234"  # Senha padrão
                
                query = """
                INSERT INTO clientes (empresa_id, nome, telefone, email, nif, endereco, codigo_cartao, senha_cartao, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                params = (1, nome, telefone, email, nif, endereco, codigo_cartao, senha_cartao)
            
            result = self.db.execute_insert(query, params)
            
            if result:
                QMessageBox.information(self, "Sucesso", "Cliente salvo com sucesso!")
                self.limpar_form_cliente()
                self.carregar_clientes()
            else:
                QMessageBox.critical(self, "Erro", "Erro ao salvar cliente!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {str(e)}")
    
    def limpar_form_cliente(self):
        """Limpa o formulário de cliente"""
        self.cliente_id = None
        self.cliente_nome.clear()
        self.cliente_telefone.clear()
        self.cliente_email.clear()
        self.cliente_nif.clear()
        self.cliente_endereco.clear()
        self.cliente_codigo_cartao.clear()
        self.cliente_senha_cartao.clear()
    
    def editar_cliente(self, cliente):
        """Preenche formulário para edição"""
        self.cliente_id = cliente['id']
        self.cliente_nome.setText(cliente['nome'])
        self.cliente_telefone.setText(cliente['telefone'] or '')
        self.cliente_email.setText(cliente['email'] or '')
        self.cliente_nif.setText(cliente['nif'] or '')
        self.cliente_endereco.setPlainText(cliente['endereco'] or '')
        self.cliente_codigo_cartao.setText(cliente['codigo_cartao'] or '')
        self.cliente_senha_cartao.clear()
        self.cliente_senha_cartao.setPlaceholderText("Deixe em branco para manter atual")
    
    def excluir_cliente(self, cliente_id):
        """Exclui cliente (desativa)"""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "Tem certeza que deseja excluir este cliente?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_insert("UPDATE clientes SET ativo = 0 WHERE id = %s", (cliente_id,))
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.carregar_clientes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir cliente: {str(e)}")
                
        # ... (outros métodos Caixa)
    def setup_caixa_tab(self, parent):
        """Aba de gestão de caixa"""
        layout = QVBoxLayout()
        
        # Controles de caixa
        controles_group = QGroupBox("Controles de Caixa")
        controles_layout = QGridLayout()
        
        self.combo_caixa = QComboBox()
        self.carregar_caixas()
        
        btn_abrir = QPushButton("🟢 Abrir Caixa")
        btn_abrir.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_abrir.clicked.connect(self.abrir_caixa)
        
        btn_fechar = QPushButton("🔴 Fechar Caixa")
        btn_fechar.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        btn_fechar.clicked.connect(self.fechar_caixa)
        
        btn_sangria = QPushButton("💰 Sangria")
        btn_sangria.setStyleSheet("background-color: #f39c12; color: white; padding: 10px;")
        btn_sangria.clicked.connect(self.sangria_caixa)
        
        btn_suprimento = QPushButton("💵 Suprimento")
        btn_suprimento.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        btn_suprimento.clicked.connect(self.suprimento_caixa)
        
        controles_layout.addWidget(QLabel("Caixa:"), 0, 0)
        controles_layout.addWidget(self.combo_caixa, 0, 1)
        controles_layout.addWidget(btn_abrir, 0, 2)
        controles_layout.addWidget(btn_fechar, 0, 3)
        controles_layout.addWidget(btn_sangria, 1, 2)
        controles_layout.addWidget(btn_suprimento, 1, 3)
        
        controles_group.setLayout(controles_layout)
        layout.addWidget(controles_group)
        
        # Status do caixa
        status_group = QGroupBox("Status do Caixa")
        status_layout = QGridLayout()
        
        self.lbl_status_caixa = QLabel("Status: Não verificado")
        self.lbl_saldo_caixa = QLabel("Saldo: 0.00 Kz")
        self.lbl_vendas_hoje = QLabel("Vendas Hoje: 0")
        self.lbl_total_hoje = QLabel("Total Hoje: 0.00 Kz")
        
        status_layout.addWidget(self.lbl_status_caixa, 0, 0)
        status_layout.addWidget(self.lbl_saldo_caixa, 0, 1)
        status_layout.addWidget(self.lbl_vendas_hoje, 1, 0)
        status_layout.addWidget(self.lbl_total_hoje, 1, 1)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Movimentos do caixa
        self.tabela_movimentos = QTableWidget()
        self.tabela_movimentos.setColumnCount(6)
        self.tabela_movimentos.setHorizontalHeaderLabels([
            "Data/Hora", "Tipo", "Valor", "Usuário", "Observação", "Status"
        ])
        layout.addWidget(self.tabela_movimentos)
        
        parent.setLayout(layout)
        self.carregar_status_caixa()
        self.carregar_movimentos_caixa()
    
    def carregar_caixas(self):
        """Carrega caixas no combo"""
        try:
            caixas = self.db.execute_query("SELECT id, nome FROM caixas WHERE ativo = 1")
            for caixa in caixas:
                self.combo_caixa.addItem(caixa['nome'], caixa['id'])
        except Exception as e:
            print(f"Erro ao carregar caixas: {e}")
    
    def carregar_status_caixa(self):
        """Carrega status do caixa"""
        try:
            # Verificar se há caixa aberto
            caixa_aberto = self.db.execute_query("""
                SELECT mc.*, u.nome as usuario_nome 
                FROM movimentos_caixa mc
                JOIN usuarios u ON mc.usuario_id = u.id
                WHERE mc.tipo = 'abertura' 
                AND DATE(mc.created_at) = CURDATE()
                ORDER BY mc.created_at DESC 
                LIMIT 1
            """)
            
            if caixa_aberto:
                self.lbl_status_caixa.setText("Status: 🟢 ABERTO")
                self.lbl_status_caixa.setStyleSheet("color: #27ae60; font-weight: bold;")
                
                # Calcular saldo atual
                saldo = self.db.execute_query("""
                    SELECT 
                        SUM(CASE WHEN tipo IN ('abertura', 'suprimento') THEN valor ELSE 0 END) -
                        SUM(CASE WHEN tipo IN ('sangria') THEN valor ELSE 0 END) as saldo
                    FROM movimentos_caixa 
                    WHERE DATE(created_at) = CURDATE()
                """)
                
                if saldo and saldo[0]['saldo']:
                    self.lbl_saldo_caixa.setText(f"Saldo: {saldo[0]['saldo']:.2f} Kz")
                else:
                    self.lbl_saldo_caixa.setText("Saldo: 0.00 Kz")
            else:
                self.lbl_status_caixa.setText("Status: 🔴 FECHADO")
                self.lbl_status_caixa.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.lbl_saldo_caixa.setText("Saldo: 0.00 Kz")
            
            # Vendas do dia
            vendas_hoje = self.obter_vendas_hoje()
            self.lbl_vendas_hoje.setText(f"Vendas Hoje: {vendas_hoje['quantidade']}")
            self.lbl_total_hoje.setText(f"Total Hoje: {vendas_hoje['total']:.2f} Kz")
            
        except Exception as e:
            print(f"Erro ao carregar status caixa: {e}")
    
    def carregar_movimentos_caixa(self):
        """Carrega movimentos do caixa"""
        try:
            movimentos = self.db.execute_query("""
                SELECT mc.*, u.nome as usuario_nome
                FROM movimentos_caixa mc
                JOIN usuarios u ON mc.usuario_id = u.id
                WHERE DATE(mc.created_at) = CURDATE()
                ORDER BY mc.created_at DESC
            """)
            
            self.tabela_movimentos.setRowCount(len(movimentos))
            
            for row, movimento in enumerate(movimentos):
                self.tabela_movimentos.setItem(row, 0, QTableWidgetItem(
                    movimento['created_at'].strftime('%d/%m %H:%M')
                ))
                self.tabela_movimentos.setItem(row, 1, QTableWidgetItem(
                    movimento['tipo'].upper()
                ))
                self.tabela_movimentos.setItem(row, 2, QTableWidgetItem(
                    f"{movimento['valor']:.2f} Kz"
                ))
                self.tabela_movimentos.setItem(row, 3, QTableWidgetItem(
                    movimento['usuario_nome']
                ))
                self.tabela_movimentos.setItem(row, 4, QTableWidgetItem(
                    movimento['observacao'] or ''
                ))
                
                # Cor baseada no tipo
                if movimento['tipo'] == 'abertura':
                    self.tabela_movimentos.item(row, 1).setBackground(QColor(39, 174, 96))
                elif movimento['tipo'] == 'sangria':
                    self.tabela_movimentos.item(row, 1).setBackground(QColor(231, 76, 60))
                elif movimento['tipo'] == 'suprimento':
                    self.tabela_movimentos.item(row, 1).setBackground(QColor(52, 152, 219))
                
        except Exception as e:
            print(f"Erro ao carregar movimentos: {e}")
    
    def abrir_caixa(self):
        """Abre o caixa"""
        try:
            caixa_id = self.combo_caixa.currentData()
            if not caixa_id:
                QMessageBox.warning(self, "Erro", "Selecione um caixa!")
                return
            
            # Verificar se já está aberto
            caixa_aberto = self.db.execute_query("""
                SELECT * FROM movimentos_caixa 
                WHERE tipo = 'abertura' AND DATE(created_at) = CURDATE()
                LIMIT 1
            """)
            
            if caixa_aberto:
                QMessageBox.warning(self, "Aviso", "Já existe um caixa aberto hoje!")
                return
            
            valor, ok = QInputDialog.getDouble(self, "Abrir Caixa", "Valor inicial:", 0.0, 0.0, 1000000.0, 2)
            
            if ok:
                observacao, ok2 = QInputDialog.getText(self, "Observação", "Observação (opcional):")
                
                query = """
                INSERT INTO movimentos_caixa (caixa_id, usuario_id, tipo, valor, observacao)
                VALUES (%s, %s, 'abertura', %s, %s)
                """
                params = (caixa_id, self.usuario_atual['id'], valor, observacao)
                
                result = self.db.execute_insert(query, params)
                
                if result:
                    QMessageBox.information(self, "Sucesso", "Caixa aberto com sucesso!")
                    self.carregar_status_caixa()
                    self.carregar_movimentos_caixa()
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao abrir caixa!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir caixa: {str(e)}")
    
    def fechar_caixa(self):
        """Fecha o caixa"""
        try:
            caixa_id = self.combo_caixa.currentData()
            if not caixa_id:
                QMessageBox.warning(self, "Erro", "Selecione um caixa!")
                return
            
            # Calcular total de vendas do dia
            vendas_hoje = self.obter_vendas_hoje()
            
            # Calcular saldo teórico
            saldo_teorico = self.db.execute_query("""
                SELECT 
                    SUM(CASE WHEN tipo IN ('abertura', 'suprimento') THEN valor ELSE 0 END) -
                    SUM(CASE WHEN tipo IN ('sangria') THEN valor ELSE 0 END) as saldo
                FROM movimentos_caixa 
                WHERE DATE(created_at) = CURDATE()
            """)
            
            saldo = saldo_teorico[0]['saldo'] if saldo_teorico and saldo_teorico[0]['saldo'] else 0
            
            # Diálogo de confirmação
            msg = f"""
            FECHAMENTO DE CAIXA
            
            💰 Vendas Hoje: {vendas_hoje['quantidade']}
            💵 Total Vendas: {vendas_hoje['total']:.2f} Kz
            🏦 Saldo em Caixa: {saldo:.2f} Kz
            
            Confirmar fechamento?
            """
            
            reply = QMessageBox.question(self, "Fechar Caixa", msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                observacao, ok = QInputDialog.getText(self, "Observação", "Observação do fechamento:")
                
                query = """
                INSERT INTO movimentos_caixa (caixa_id, usuario_id, tipo, valor, observacao)
                VALUES (%s, %s, 'fecho', %s, %s)
                """
                params = (caixa_id, self.usuario_atual['id'], saldo, observacao)
                
                result = self.db.execute_insert(query, params)
                
                if result:
                    QMessageBox.information(self, "Sucesso", "Caixa fechado com sucesso!")
                    self.carregar_status_caixa()
                    self.carregar_movimentos_caixa()
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao fechar caixa!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao fechar caixa: {str(e)}")
    
    def sangria_caixa(self):
        """Realiza sangria do caixa"""
        try:
            caixa_id = self.combo_caixa.currentData()
            if not caixa_id:
                QMessageBox.warning(self, "Erro", "Selecione um caixa!")
                return
            
            valor, ok = QInputDialog.getDouble(self, "Sangria", "Valor da sangria:", 0.0, 0.0, 1000000.0, 2)
            
            if ok and valor > 0:
                observacao, ok2 = QInputDialog.getText(self, "Motivo", "Motivo da sangria:")
                
                query = """
                INSERT INTO movimentos_caixa (caixa_id, usuario_id, tipo, valor, observacao)
                VALUES (%s, %s, 'sangria', %s, %s)
                """
                params = (caixa_id, self.usuario_atual['id'], valor, observacao)
                
                result = self.db.execute_insert(query, params)
                
                if result:
                    QMessageBox.information(self, "Sucesso", "Sangria realizada com sucesso!")
                    self.carregar_status_caixa()
                    self.carregar_movimentos_caixa()
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao realizar sangria!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar sangria: {str(e)}")
    
    def suprimento_caixa(self):
        """Realiza suprimento do caixa"""
        try:
            caixa_id = self.combo_caixa.currentData()
            if not caixa_id:
                QMessageBox.warning(self, "Erro", "Selecione um caixa!")
                return
            
            valor, ok = QInputDialog.getDouble(self, "Suprimento", "Valor do suprimento:", 0.0, 0.0, 1000000.0, 2)
            
            if ok and valor > 0:
                observacao, ok2 = QInputDialog.getText(self, "Origem", "Origem do suprimento:")
                
                query = """
                INSERT INTO movimentos_caixa (caixa_id, usuario_id, tipo, valor, observacao)
                VALUES (%s, %s, 'suprimento', %s, %s)
                """
                params = (caixa_id, self.usuario_atual['id'], valor, observacao)
                
                result = self.db.execute_insert(query, params)
                
                if result:
                    QMessageBox.information(self, "Sucesso", "Suprimento realizado com sucesso!")
                    self.carregar_status_caixa()
                    self.carregar_movimentos_caixa()
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao realizar suprimento!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar suprimento: {str(e)}")
            
            # Promoções
            
    def setup_promocoes_tab(self, parent):
        """Aba de gestão de promoções"""
        layout = QVBoxLayout()
        
        # Formulário
        form_group = QGroupBox("Adicionar/Editar Promoção")
        form_layout = QFormLayout()
        
        self.promocao_id = None
        
        self.promocao_nome = QLineEdit()
        self.promocao_tipo = QComboBox()
        self.promocao_tipo.addItems(["Percentagem", "Valor Fixo", "Produto Grátis"])
        self.promocao_valor = QDoubleSpinBox()
        self.promocao_valor.setMaximum(1000000.00)
        self.promocao_valor.setDecimals(2)
        
        self.promocao_data_inicio = QDateEdit()
        self.promocao_data_inicio.setDate(QDate.currentDate())
        self.promocao_data_inicio.setCalendarPopup(True)
        
        self.promocao_data_fim = QDateEdit()
        self.promocao_data_fim.setDate(QDate.currentDate().addDays(7))
        self.promocao_data_fim.setCalendarPopup(True)
        
        self.promocao_ativa = QCheckBox("Promoção Ativa")
        self.promocao_ativa.setChecked(True)
        
        # Produtos aplicáveis
        self.lista_produtos = QListWidget()
        self.carregar_produtos_promocao()
        
        form_layout.addRow("Nome:*", self.promocao_nome)
        form_layout.addRow("Tipo:*", self.promocao_tipo)
        form_layout.addRow("Valor:*", self.promocao_valor)
        form_layout.addRow("Data Início:*", self.promocao_data_inicio)
        form_layout.addRow("Data Fim:*", self.promocao_data_fim)
        form_layout.addRow("", self.promocao_ativa)
        form_layout.addRow("Produtos Aplicáveis:", self.lista_produtos)
        
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar Promoção")
        btn_salvar.clicked.connect(self.salvar_promocao)
        btn_limpar = QPushButton("🗑️ Limpar")
        btn_limpar.clicked.connect(self.limpar_form_promocao)
        
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_limpar)
        form_layout.addRow(btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Lista de promoções
        self.tabela_promocoes = QTableWidget()
        self.tabela_promocoes.setColumnCount(7)
        self.tabela_promocoes.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Valor", "Período", "Estado", "Ações"
        ])
        layout.addWidget(self.tabela_promocoes)
        
        parent.setLayout(layout)
        self.carregar_promocoes()
    
    def carregar_produtos_promocao(self):
        """Carrega produtos para a lista de promoções"""
        try:
            produtos = self.db.execute_query("""
                SELECT id, nome, preco_venda FROM produtos WHERE ativo = 1 ORDER BY nome
            """)
            
            self.lista_produtos.clear()
            for produto in produtos:
                item_text = f"{produto['nome']} - {produto['preco_venda']:.2f} Kz"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, produto['id'])
                self.lista_produtos.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
    
    def carregar_promocoes(self):
        """Carrega promoções na tabela"""
        try:
            promocoes = self.db.execute_query("""
                SELECT * FROM promocoes 
                WHERE ativo = 1 
                ORDER BY data_inicio DESC
            """)
            
            self.tabela_promocoes.setRowCount(len(promocoes))
            
            for row, promocao in enumerate(promocoes):
                self.tabela_promocoes.setItem(row, 0, QTableWidgetItem(str(promocao['id'])))
                self.tabela_promocoes.setItem(row, 1, QTableWidgetItem(promocao['nome']))
                self.tabela_promocoes.setItem(row, 2, QTableWidgetItem(promocao['tipo']))
                self.tabela_promocoes.setItem(row, 3, QTableWidgetItem(f"{promocao['valor']:.2f}"))
                
                periodo = f"{promocao['data_inicio']} a {promocao['data_fim']}"
                self.tabela_promocoes.setItem(row, 4, QTableWidgetItem(periodo))
                
                # Verificar se está ativa
                hoje = QDate.currentDate().toString('yyyy-MM-dd')
                if promocao['data_inicio'] <= hoje <= promocao['data_fim'] and promocao['ativo']:
                    estado = "🟢 Ativa"
                else:
                    estado = "🔴 Inativa"
                self.tabela_promocoes.setItem(row, 5, QTableWidgetItem(estado))
                
                # Botões de ação
                btn_editar = QPushButton("✏️")
                btn_editar.setStyleSheet("background-color: #3498db; color: white; border: none; padding: 5px;")
                btn_editar.clicked.connect(lambda checked, p=promocao: self.editar_promocao(p))
                
                btn_excluir = QPushButton("🗑️")
                btn_excluir.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 5px;")
                btn_excluir.clicked.connect(lambda checked, pid=promocao['id']: self.excluir_promocao(pid))
                
                acoes_widget = QWidget()
                acoes_layout = QHBoxLayout()
                acoes_layout.addWidget(btn_editar)
                acoes_layout.addWidget(btn_excluir)
                acoes_layout.setContentsMargins(0, 0, 0, 0)
                acoes_widget.setLayout(acoes_layout)
                
                self.tabela_promocoes.setCellWidget(row, 6, acoes_widget)
                
        except Exception as e:
            print(f"Erro ao carregar promoções: {e}")
    
    def salvar_promocao(self):
        """Salva ou atualiza promoção"""
        try:
            nome = self.promocao_nome.text().strip()
            tipo = self.promocao_tipo.currentText().lower()
            valor = self.promocao_valor.value()
            data_inicio = self.promocao_data_inicio.date().toString('yyyy-MM-dd')
            data_fim = self.promocao_data_fim.date().toString('yyyy-MM-dd')
            ativa = self.promocao_ativa.isChecked()
            
            if not nome:
                QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
                return
            
            # Obter produtos selecionados
            produtos_selecionados = []
            for i in range(self.lista_produtos.count()):
                if self.lista_produtos.item(i).isSelected():
                    produto_id = self.lista_produtos.item(i).data(Qt.UserRole)
                    produtos_selecionados.append(produto_id)
            
            produtos_json = json.dumps(produtos_selecionados)
            
            if self.promocao_id:  # Edição
                query = """
                UPDATE promocoes 
                SET nome = %s, tipo = %s, valor = %s, data_inicio = %s, 
                    data_fim = %s, ativo = %s, produtos_aplicaveis = %s
                WHERE id = %s
                """
                params = (nome, tipo, valor, data_inicio, data_fim, ativa, produtos_json, self.promocao_id)
            else:  # Nova promoção
                query = """
                INSERT INTO promocoes (empresa_id, nome, tipo, valor, data_inicio, data_fim, ativo, produtos_aplicaveis)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (1, nome, tipo, valor, data_inicio, data_fim, ativa, produtos_json)
            
            result = self.db.execute_insert(query, params)
            
            if result:
                QMessageBox.information(self, "Sucesso", "Promoção salva com sucesso!")
                self.limpar_form_promocao()
                self.carregar_promocoes()
            else:
                QMessageBox.critical(self, "Erro", "Erro ao salvar promoção!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar promoção: {str(e)}")
    
    def limpar_form_promocao(self):
        """Limpa o formulário de promoção"""
        self.promocao_id = None
        self.promocao_nome.clear()
        self.promocao_tipo.setCurrentIndex(0)
        self.promocao_valor.setValue(0.0)
        self.promocao_data_inicio.setDate(QDate.currentDate())
        self.promocao_data_fim.setDate(QDate.currentDate().addDays(7))
        self.promocao_ativa.setChecked(True)
        self.lista_produtos.clearSelection()
    
    def editar_promocao(self, promocao):
        """Preenche formulário para edição"""
        self.promocao_id = promocao['id']
        self.promocao_nome.setText(promocao['nome'])
        
        # Definir tipo
        index = self.promocao_tipo.findText(promocao['tipo'].title())
        if index >= 0:
            self.promocao_tipo.setCurrentIndex(index)
        
        self.promocao_valor.setValue(float(promocao['valor']))
        self.promocao_data_inicio.setDate(QDate.fromString(promocao['data_inicio'], 'yyyy-MM-dd'))
        self.promocao_data_fim.setDate(QDate.fromString(promocao['data_fim'], 'yyyy-MM-dd'))
        self.promocao_ativa.setChecked(bool(promocao['ativo']))
        
        # Selecionar produtos
        if promocao['produtos_aplicaveis']:
            try:
                produtos_ids = json.loads(promocao['produtos_aplicaveis'])
                for i in range(self.lista_produtos.count()):
                    produto_id = self.lista_produtos.item(i).data(Qt.UserRole)
                    if produto_id in produtos_ids:
                        self.lista_produtos.item(i).setSelected(True)
            except:
                pass
    
    def excluir_promocao(self, promocao_id):
        """Exclui promoção"""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "Tem certeza que deseja excluir esta promoção?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_insert("UPDATE promocoes SET ativo = 0 WHERE id = %s", (promocao_id,))
                QMessageBox.information(self, "Sucesso", "Promoção excluída com sucesso!")
                self.carregar_promocoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir promoção: {str(e)}")
    
        # Outros
    def setup_config_tab(self, parent):
        """Aba de configurações do sistema"""
        layout = QVBoxLayout()
        
        # Configurações da Empresa
        empresa_group = QGroupBox("Configurações da Empresa")
        empresa_layout = QFormLayout()
        
        self.config_empresa_nome = QLineEdit()
        self.config_empresa_nif = QLineEdit()
        self.config_empresa_telefone = QLineEdit()
        self.config_empresa_email = QLineEdit()
        self.config_empresa_endereco = QTextEdit()
        self.config_empresa_endereco.setMaximumHeight(80)
        
        empresa_layout.addRow("Nome da Empresa:*", self.config_empresa_nome)
        empresa_layout.addRow("NIF:*", self.config_empresa_nif)
        empresa_layout.addRow("Telefone:*", self.config_empresa_telefone)
        empresa_layout.addRow("Email:", self.config_empresa_email)
        empresa_layout.addRow("Endereço:", self.config_empresa_endereco)
        
        empresa_group.setLayout(empresa_layout)
        layout.addWidget(empresa_group)
        
        # Configurações do Sistema
        sistema_group = QGroupBox("Configurações do Sistema")
        sistema_layout = QFormLayout()
        
        self.config_iva_activo = QCheckBox("IVA Ativo")
        self.config_iva_activo.setChecked(True)
        
        self.config_troco_activo = QCheckBox("Troco Ativo")
        self.config_troco_activo.setChecked(True)
        
        self.config_som_activo = QCheckBox("Som Ativo")
        self.config_som_activo.setChecked(True)
        
        self.config_logs_activo = QCheckBox("Logs Ativos")
        self.config_logs_activo.setChecked(True)
        
        sistema_layout.addRow("", self.config_iva_activo)
        sistema_layout.addRow("", self.config_troco_activo)
        sistema_layout.addRow("", self.config_som_activo)
        sistema_layout.addRow("", self.config_logs_activo)
        
        sistema_group.setLayout(sistema_layout)
        layout.addWidget(sistema_group)
        
        # Configurações da Impressora
        impressora_group = QGroupBox("Configurações da Impressora")
        impressora_layout = QFormLayout()
        
        self.config_impressora_tipo = QComboBox()
        self.config_impressora_tipo.addItems(["Windows", "USB", "COM", "Ethernet"])
        
        self.config_impressora_nome = QLineEdit()
        self.config_impressora_porta = QLineEdit()
        
        self.config_impressora_automatica = QCheckBox("Impressão Automática")
        self.config_impressora_automatica.setChecked(True)
        
        impressora_layout.addRow("Tipo:", self.config_impressora_tipo)
        impressora_layout.addRow("Nome:", self.config_impressora_nome)
        impressora_layout.addRow("Porta:", self.config_impressora_porta)
        impressora_layout.addRow("", self.config_impressora_automatica)
        
        impressora_group.setLayout(impressora_layout)
        layout.addWidget(impressora_group)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_carregar = QPushButton("📥 Carregar Configurações")
        btn_carregar.clicked.connect(self.carregar_configuracoes)
        
        btn_salvar = QPushButton("💾 Salvar Configurações")
        btn_salvar.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_salvar.clicked.connect(self.salvar_configuracoes)
        
        btn_limpar = QPushButton("🗑️ Limpar")
        btn_limpar.clicked.connect(self.limpar_configuracoes)
        
        btn_layout.addWidget(btn_carregar)
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_limpar)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        parent.setLayout(layout)
        self.carregar_configuracoes()
    
    def carregar_configuracoes(self):
        """Carrega configurações atuais"""
        try:
            # Carregar configurações da empresa
            empresa = self.db.execute_query("SELECT * FROM empresas WHERE id = 1")
            if empresa:
                emp = empresa[0]
                self.config_empresa_nome.setText(emp['nome'])
                self.config_empresa_nif.setText(emp['nif'] or '')
                self.config_empresa_telefone.setText(emp['telefone'] or '')
                self.config_empresa_email.setText(emp['email'] or '')
                self.config_empresa_endereco.setPlainText(emp['endereco'] or '')
            
            # Carregar configurações do sistema
            configuracoes = self.db.execute_query("SELECT chave, valor FROM configuracoes WHERE empresa_id = 1")
            config_dict = {cfg['chave']: cfg['valor'] for cfg in configuracoes}
            
            self.config_iva_activo.setChecked(config_dict.get('iva_activo', 'true').lower() == 'true')
            self.config_troco_activo.setChecked(config_dict.get('troco_activo', 'true').lower() == 'true')
            self.config_som_activo.setChecked(config_dict.get('som_activo', 'true').lower() == 'true')
            self.config_logs_activo.setChecked(config_dict.get('logs_activo', 'true').lower() == 'true')
            self.config_impressora_automatica.setChecked(config_dict.get('impressao_automatica', 'true').lower() == 'true')
            
            # Configurações da impressora
            index = self.config_impressora_tipo.findText(config_dict.get('impressora_tipo', 'Windows'))
            if index >= 0:
                self.config_impressora_tipo.setCurrentIndex(index)
            
            self.config_impressora_nome.setText(config_dict.get('impressora_nome', ''))
            self.config_impressora_porta.setText(config_dict.get('impressora_porta', ''))
            
            QMessageBox.information(self, "Sucesso", "Configurações carregadas com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar configurações: {str(e)}")
    
    def salvar_configuracoes(self):
        """Salva configurações do sistema"""
        try:
            # Validar campos obrigatórios
            if not self.config_empresa_nome.text().strip():
                QMessageBox.warning(self, "Erro", "Nome da empresa é obrigatório!")
                return
            
            # Atualizar empresa
            query_empresa = """
            UPDATE empresas 
            SET nome = %s, nif = %s, telefone = %s, email = %s, endereco = %s
            WHERE id = 1
            """
            params_empresa = (
                self.config_empresa_nome.text().strip(),
                self.config_empresa_nif.text().strip(),
                self.config_empresa_telefone.text().strip(),
                self.config_empresa_email.text().strip(),
                self.config_empresa_endereco.toPlainText().strip()
            )
            
            self.db.execute_insert(query_empresa, params_empresa)
            
            # Configurações do sistema
            configuracoes = {
                'iva_activo': str(self.config_iva_activo.isChecked()).lower(),
                'troco_activo': str(self.config_troco_activo.isChecked()).lower(),
                'som_activo': str(self.config_som_activo.isChecked()).lower(),
                'logs_activo': str(self.config_logs_activo.isChecked()).lower(),
                'impressao_automatica': str(self.config_impressora_automatica.isChecked()).lower(),
                'impressora_tipo': self.config_impressora_tipo.currentText(),
                'impressora_nome': self.config_impressora_nome.text().strip(),
                'impressora_porta': self.config_impressora_porta.text().strip()
            }
            
            # Salvar configurações
            for chave, valor in configuracoes.items():
                query = """
                INSERT INTO configuracoes (empresa_id, chave, valor) 
                VALUES (1, %s, %s)
                ON DUPLICATE KEY UPDATE valor = %s
                """
                self.db.execute_insert(query, (chave, valor, valor))
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def limpar_configuracoes(self):
        """Limpa o formulário de configurações"""
        self.config_empresa_nome.clear()
        self.config_empresa_nif.clear()
        self.config_empresa_telefone.clear()
        self.config_empresa_email.clear()
        self.config_empresa_endereco.clear()
        self.config_iva_activo.setChecked(True)
        self.config_troco_activo.setChecked(True)
        self.config_som_activo.setChecked(True)
        self.config_logs_activo.setChecked(True)
        self.config_impressora_tipo.setCurrentIndex(0)
        self.config_impressora_nome.clear()
        self.config_impressora_porta.clear()
        self.config_impressora_automatica.setChecked(True)