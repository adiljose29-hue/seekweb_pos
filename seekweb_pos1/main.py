#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget
from PyQt5.QtCore import QSettings
import mysql.connector
from core.database import Database
from core.config import Config
from gui.login import LoginWindow
from gui.vendas import VendasWindow
from gui.admin import AdminWindow

class SeekWebPOS(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            self.config = Config()
            self.db = Database(self.config)
            self.usuario_atual = None
            self.setup_ui()
        except Exception as e:
            QMessageBox.critical(None, "Erro de Inicialização", 
                               f"Erro ao iniciar sistema: {str(e)}\n\n"
                               "Verifique se:\n"
                               "1. MySQL está instalado e rodando\n"
                               "2. A base de dados 'bd_seekweb' existe\n"
                               "3. As credenciais no config.ini estão corretas")
            raise
        
    def setup_ui(self):
        self.setWindowTitle("SeekWeb POS - Sistema de Vendas")
        self.setGeometry(100, 100, 1200, 700)  # Tamanho menor para melhor visualização
        
        # Widget central empilhado
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Janelas
        self.login_window = LoginWindow(self.db, self)
        self.vendas_window = VendasWindow(self.db, self)
        self.admin_window = AdminWindow(self.db, self)
        
        # Adicionar às stacks
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.vendas_window)
        self.stacked_widget.addWidget(self.admin_window)
        
        # Mostrar login inicialmente
        self.stacked_widget.setCurrentWidget(self.login_window)
        
        # Conectar sinais
        self.login_window.login_successful.connect(self.on_login_successful)
        self.vendas_window.logout_requested.connect(self.on_logout)
        self.admin_window.logout_requested.connect(self.on_logout)
    
    def on_login_successful(self, usuario):
        self.usuario_atual = usuario
        nivel = usuario['nivel_id']
        
        print(f"🔍 Login successful - Usuário: {usuario['nome']}, Nível: {nivel}")
        
        if nivel == 1:  # Administrador
            self.stacked_widget.setCurrentWidget(self.admin_window)
            # CORREÇÃO: Passar usuario_atual para a janela admin
            self.admin_window.usuario_atual = usuario
            self.admin_window.carregar_dados()
        elif nivel == 2:  # Supervisor
            self.stacked_widget.setCurrentWidget(self.vendas_window)
            # CORREÇÃO: Passar usuario_atual para a janela de vendas
            self.vendas_window.usuario_atual = usuario
            self.vendas_window.carregar_dados()
        else:  # Vendedor
            self.stacked_widget.setCurrentWidget(self.vendas_window)
            # CORREÇÃO: Passar usuario_atual para a janela de vendas
            self.vendas_window.usuario_atual = usuario
            self.vendas_window.carregar_dados()
    
    def on_logout(self):
        self.usuario_atual = None
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.login_window.limpar_campos()

def main():
    app = QApplication(sys.argv)
    
    # Verificar conexão com base de dados
    try:
        window = SeekWebPOS()
        window.show()
    except Exception as e:
        print(f"Erro fatal: {e}")
        return 1
    
    return app.exec_()

# No final da classe SeekWebPOS, adicione:
def closeEvent(self, event):
    """Evento chamado quando a aplicação é fechada"""
    # Fechar scanner se estiver ativo
    current_widget = self.stacked_widget.currentWidget()
    if hasattr(current_widget, 'scanner'):
        current_widget.scanner.fechar()
    event.accept()

if __name__ == "__main__":
    sys.exit(main())