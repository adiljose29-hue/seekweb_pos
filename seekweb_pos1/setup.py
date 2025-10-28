#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import mysql.connector
from mysql.connector import Error
import configparser

def install_dependencies():
    """Instala dependências do Python"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_database_schema():
    """Cria a base de dados e tabelas"""
    print("🗄️ Criando base de dados...")
    
    try:
        # Conectar ao MySQL (sem especificar base de dados)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        cursor = conn.cursor()
        
        # Criar base de dados
        cursor.execute("CREATE DATABASE IF NOT EXISTS bd_seekweb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Base de dados criada!")
        
        cursor.execute("USE bd_seekweb")
        
        # Executar script SQL
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Executar comandos SQL
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("✅ Tabelas criadas com sucesso!")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Erro ao criar base de dados: {e}")
        return False

def create_config_file():
    """Cria ficheiro de configuração"""
    print("⚙️ Criando ficheiro de configuração...")
    
    config = configparser.ConfigParser()
    
    # Secção Database
    config['Database'] = {
        'host': 'localhost',
        'user': 'root', 
        'password': '',
        'database': 'bd_seekweb',
        'port': '3306'
    }
    
    # Secção Impressora
    config['Impressora'] = {
        'tipo': 'windows',
        'porta': '',
        'nome_impressora': 'Microsoft Print to PDF',
        'gaveta_activa': 'true',
        'corte_papel': 'true',
        'largura_papel': '80'
    }
    
    # Secção Recibo
    config['Recibo'] = {
        'empresa_nome': 'SeekWeb Comércio',
        'empresa_nif': '5000000000',
        'empresa_telefone': '+244 123 456 789',
        'empresa_endereco': 'Luanda, Angola',
        'cabecalho': '**SEEKWEB COMÉRCIO**',
        'rodape': 'Obrigado pela sua preferência!',
        'mostrar_vendedor': 'true',
        'mostrar_data': 'true',
        'mostrar_iva': 'true'
    }
    
    # Secção Audio
    config['Audio'] = {
        'activo': 'true',
        'volume': '80',
        'som_venda': 'venda.wav',
        'som_erro': 'erro.wav'
    }
    
    # Secção Scanner
    config['Scanner'] = {
        'tipo': 'usb',
        'porta_usb': '',
        'porta_com': 'COM1',
        'velocidade': '9600'
    }
    
    # Secção Caixa
    config['Caixa'] = {
        'moeda': 'Kz',
        'iva_activo': 'true',
        'troco_activo': 'true',
        'local_recibos': 'recibos/',
        'logs_activo': 'true'
    }
    
    # Secção Seguranca
    config['Seguranca'] = {
        'nivel_vendedor': '3',
        'codigo_barras_supervisor': 'SUP001',
        'tempo_sessao': '3600'
    }
    
    # Secção BoxesProdutos
    config['BoxesProdutos'] = {
        'quantidade_boxes': '6',
        'box1_nome': 'Eletrónica',
        'box1_cor': '#FF5733',
        'box1_produtos': '1,2,3',
        'box2_nome': 'Informática', 
        'box2_cor': '#33FF57',
        'box2_produtos': '3,4',
        'box3_nome': 'Escritório',
        'box3_cor': '#3357FF',
        'box3_produtos': '5,6'
    }
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("✅ Ficheiro config.ini criado!")

def create_directories():
    """Cria diretórios necessários"""
    print("📁 Criando diretórios...")
    
    directories = ['recibos', 'logs', 'sons']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Diretório {directory}/ criado")
        else:
            print(f"✅ Diretório {directory}/ já existe")

def main():
    """Função principal de setup"""
    print("🚀 CONFIGURAÇÃO DO SISTEMA SEEKWEB POS")
    print("=" * 50)
    
    # Criar diretórios
    create_directories()
    
    # Criar ficheiro de configuração
    create_config_file()
    
    # Instalar dependências
    if install_dependencies():
        # Criar base de dados
        if create_database_schema():
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n📝 PARA INICIAR O SISTEMA:")
            print("   python main.py")
            print("\n🔑 CREDENCIAIS DE TESTE:")
            print("   Admin: admin@seekweb.com / admin123")
            print("   Supervisor: supervisor@seekweb.com / super123") 
            print("   Vendedor: vendedor@seekweb.com / vend123")
        else:
            print("\n❌ Erro na configuração da base de dados")
    else:
        print("\n❌ Erro na instalação de dependências")

if __name__ == "__main__":
    main()