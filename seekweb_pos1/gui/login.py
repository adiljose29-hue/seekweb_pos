from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap

class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Title
        title = QLabel("SeekWeb POS")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Sistema de Vendas")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Espaço
        layout.addSpacing(30)
        
        # Login Frame
        login_frame = QFrame()
        login_frame.setFixedSize(400, 300)
        login_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(30, 30, 30, 30)
        
        # Email
        frame_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu email")
        frame_layout.addWidget(self.email_input)
        
        # Senha
        frame_layout.addWidget(QLabel("Senha:"))
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Digite sua senha")
        self.senha_input.setEchoMode(QLineEdit.Password)
        frame_layout.addWidget(self.senha_input)
        
        # Espaço
        frame_layout.addSpacing(20)
        
        # Botão Login
        login_btn = QPushButton("Entrar")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        login_btn.clicked.connect(self.fazer_login)
        frame_layout.addWidget(login_btn)
        
        # Informação de teste
        info_label = QLabel("💡 Use: admin@seekweb.com / admin123")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 15px;")
        frame_layout.addWidget(info_label)
        
        login_frame.setLayout(frame_layout)
        layout.addWidget(login_frame)
        
        self.setLayout(layout)
        
        # Conectar Enter para login
        self.senha_input.returnPressed.connect(self.fazer_login)
        
        # Preencher automaticamente para teste
        self.email_input.setText("admin@seekweb.com")
        self.senha_input.setText("admin123")
    
    def fazer_login(self):
        email = self.email_input.text().strip()
        senha = self.senha_input.text().strip()
        
        if not email or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha email e senha")
            return
        
        # Simular autenticação - EM PRODUÇÃO, usar a classe Usuario
        try:
            query = """
            SELECT u.*, n.nome as nivel_nome, n.permissoes 
            FROM usuarios u 
            JOIN niveis_usuario n ON u.nivel_id = n.id 
            WHERE u.email = %s AND u.senha = %s AND u.ativo = 1
            """
            result = self.db.execute_query(query, (email, senha))
            
            if result:
                usuario = result[0]
                self.login_successful.emit(usuario)
            else:
                QMessageBox.critical(self, "Erro", "Credenciais inválidas")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na autenticação: {str(e)}")
    
    def limpar_campos(self):
        self.email_input.clear()
        self.senha_input.clear()