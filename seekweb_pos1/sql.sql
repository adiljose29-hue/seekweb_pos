-- Criar base de dados
CREATE DATABASE IF NOT EXISTS bd_seekweb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_seekweb;

-- Tabela de empresas
CREATE TABLE empresas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255) NOT NULL,
    nif VARCHAR(50),
    telefone VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    logo_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de caixas
CREATE TABLE caixas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    localizacao VARCHAR(255),
    impressora_tipo ENUM('windows', 'usb', 'com', 'ethernet') DEFAULT 'windows',
    impressora_porta VARCHAR(255),
    gaveta_dinheiro BOOLEAN DEFAULT TRUE,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de níveis de usuário
CREATE TABLE niveis_usuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    permissoes JSON
);

-- Tabela de usuários
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nivel_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, -- Será encriptada posteriormente
    codigo_barras VARCHAR(100) UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (nivel_id) REFERENCES niveis_usuario(id)
);

-- Tabela de taxas IVA
CREATE TABLE taxas_iva (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    taxa DECIMAL(5,2) NOT NULL,
    descricao VARCHAR(100) NOT NULL,
    codigo VARCHAR(20),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de categorias de produtos
CREATE TABLE categorias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de produtos
CREATE TABLE produtos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    categoria_id INT,
    taxa_iva_id INT NOT NULL,
    codigo_barras VARCHAR(100) UNIQUE,
    referencia VARCHAR(100),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    preco_compra DECIMAL(10,2) NOT NULL,
    preco_venda DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    stock_minimo INT DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    imagem_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (taxa_iva_id) REFERENCES taxas_iva(id)
);

-- Tabela de clientes
CREATE TABLE clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    nif VARCHAR(50),
    endereco TEXT,
    codigo_cartao VARCHAR(100) UNIQUE,
    senha_cartao VARCHAR(255),
    pontos_fidelidade INT DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de formas de pagamento
CREATE TABLE formas_pagamento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    aceita_troco BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de vendas
CREATE TABLE vendas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    caixa_id INT NOT NULL,
    usuario_id INT NOT NULL,
    cliente_id INT,
    numero_venda VARCHAR(50) UNIQUE NOT NULL,
    total_sem_iva DECIMAL(10,2) NOT NULL,
    total_iva DECIMAL(10,2) NOT NULL,
    total_com_iva DECIMAL(10,2) NOT NULL,
    troco DECIMAL(10,2) DEFAULT 0,
    estado ENUM('pendente', 'paga', 'cancelada', 'devolvida') DEFAULT 'pendente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (caixa_id) REFERENCES caixas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Tabela de itens de venda
CREATE TABLE venda_itens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    venda_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    taxa_iva_id INT NOT NULL,
    valor_iva DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    desconto DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (taxa_iva_id) REFERENCES taxas_iva(id)
);

-- Tabela de pagamentos da venda
CREATE TABLE venda_pagamentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    venda_id INT NOT NULL,
    forma_pagamento_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    troco DECIMAL(10,2) DEFAULT 0,
    referencia VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento(id)
);

-- Tabela de promoções
CREATE TABLE promocoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo ENUM('percentagem', 'valor_fixo', 'produto_gratis') NOT NULL,
    valor DECIMAL(10,2),
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    produtos_aplicaveis JSON, -- IDs dos produtos ou categorias
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

-- Tabela de movimentos de caixa
CREATE TABLE movimentos_caixa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    caixa_id INT NOT NULL,
    usuario_id INT NOT NULL,
    tipo ENUM('abertura', 'fecho', 'sangria', 'suprimento') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caixa_id) REFERENCES caixas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de devoluções
CREATE TABLE devolucoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    venda_original_id INT NOT NULL,
    usuario_id INT NOT NULL,
    supervisor_id INT,
    motivo TEXT,
    valor_devolvido DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venda_original_id) REFERENCES vendas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (supervisor_id) REFERENCES usuarios(id)
);

-- Tabela de itens devolvidos
CREATE TABLE devolucao_itens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    devolucao_id INT NOT NULL,
    venda_item_id INT NOT NULL,
    quantidade INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (devolucao_id) REFERENCES devolucoes(id) ON DELETE CASCADE,
    FOREIGN KEY (venda_item_id) REFERENCES venda_itens(id)
);

-- Tabela de logs do sistema
CREATE TABLE logs_sistema (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT,
    acao VARCHAR(255) NOT NULL,
    descricao TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de configurações
CREATE TABLE configuracoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresa_id INT NOT NULL,
    chave VARCHAR(255) NOT NULL,
    valor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    UNIQUE KEY unique_empresa_chave (empresa_id, chave)
);


-- Inserir dados iniciais
USE bd_seekweb;

-- Inserir empresa
INSERT INTO empresas (nome, nif, telefone, email, endereco) VALUES 
('SeekWeb Comércio', '5000000000', '+244 123 456 789', 'info@seekweb.com', 'Luanda, Angola');

-- Inserir níveis de usuário
INSERT INTO niveis_usuario (nome, descricao, permissoes) VALUES 
('Administrador', 'Acesso total ao sistema', '{"vendas": true, "relatorios": true, "configuracoes": true, "usuarios": true, "produtos": true, "clientes": true, "caixa": true}'),
('Supervisor', 'Supervisão e autorizações', '{"vendas": true, "relatorios": true, "configuracoes": false, "usuarios": false, "produtos": true, "clientes": true, "caixa": true, "autorizar_devolucoes": true, "sangria": true}'),
('Vendedor', 'Apenas vendas', '{"vendas": true, "relatorios": false, "configuracoes": false, "usuarios": false, "produtos": true, "clientes": true, "caixa": false}');

-- Inserir usuários
INSERT INTO usuarios (empresa_id, nivel_id, nome, email, senha, codigo_barras) VALUES 
(1, 1, 'Administrador', 'admin@seekweb.com', 'admin123', 'SUP001'),
(1, 2, 'Supervisor', 'supervisor@seekweb.com', 'super123', 'SUP002'),
(1, 3, 'Vendedor', 'vendedor@seekweb.com', 'vend123', 'VEN001');

-- Inserir taxas IVA (Norma Angola AGT)
INSERT INTO taxas_iva (empresa_id, taxa, descricao, codigo) VALUES 
(1, 14.00, 'IVA Normal 14%', 'IVA14'),
(1, 7.00, 'IVA Reduzido 7%', 'IVA7'),
(1, 5.00, 'IVA Super Reduzido 5%', 'IVA5'),
(1, 0.00, 'Isento de IVA', 'ISENTO');

-- Inserir categorias
INSERT INTO categorias (empresa_id, nome, descricao) VALUES 
(1, 'Electrónica', 'Produtos electrónicos'),
(1, 'Informática', 'Computadores e acessórios'),
(1, 'Telefonia', 'Telemóveis e tablets'),
(1, 'Escritório', 'Material de escritório');

-- Inserir formas de pagamento
INSERT INTO formas_pagamento (empresa_id, nome, codigo, aceita_troco) VALUES 
(1, 'Dinheiro', 'DINHEIRO', TRUE),
(1, 'Cartão Débito', 'CARTAO_DEBITO', FALSE),
(1, 'Cartão Crédito', 'CARTAO_CREDITO', FALSE),
(1, 'Transferência', 'TRANSFERENCIA', FALSE),
(1, 'Cartão Cliente', 'CARTAO_CLIENTE', FALSE);

-- Inserir caixas
INSERT INTO caixas (empresa_id, nome, localizacao, impressora_tipo) VALUES 
(1, 'Caixa 1', 'Loja Principal - Balcão 1', 'windows'),
(1, 'Caixa 2', 'Loja Principal - Balcão 2', 'usb');

-- Inserir produtos de exemplo
INSERT INTO produtos (empresa_id, categoria_id, taxa_iva_id, codigo_barras, referencia, nome, descricao, preco_compra, preco_venda, stock) VALUES 
(1, 1, 1, '7891234567890', 'SMX001', 'Smartphone X', 'Smartphone Android 128GB', 15000.00, 25000.00, 50),
(1, 1, 1, '7891234567891', 'TAB001', 'Tablet Pro', 'Tablet 10 polegadas 64GB', 8000.00, 15000.00, 30),
(1, 2, 1, '7891234567892', 'LAP001', 'Laptop Business', 'Laptop Intel i5 8GB RAM', 35000.00, 50000.00, 20),
(1, 2, 1, '7891234567893', 'MOUSE001', 'Mouse Óptico', 'Mouse USB óptico', 500.00, 1500.00, 100),
(1, 4, 2, '7891234567894', 'CAD001', 'Caderno A4', 'Caderno 200 folhas', 300.00, 800.00, 200),
(1, 4, 2, '7891234567895', 'CAN001', 'Caneta Esferográfica', 'Caneta azul ponta fina', 50.00, 200.00, 500);

-- Inserir clientes exemplo
INSERT INTO clientes (empresa_id, nome, telefone, email, nif, codigo_cartao, senha_cartao, pontos_fidelidade) VALUES 
(1, 'Cliente Frequente', '+244 923 456 789', 'cliente@email.com', '123456789LA', 'CLI001', '1234', 150),
(1, 'Maria Silva', '+244 924 567 890', 'maria@email.com', '987654321LA', 'CLI002', '5678', 75);

-- Inserir configurações padrão
INSERT INTO configuracoes (empresa_id, chave, valor) VALUES 
(1, 'moeda', 'Kz'),
(1, 'iva_activo', 'true'),
(1, 'som_activo', 'true'),
(1, 'local_recibos', '/recibos/'),
(1, 'logs_activo', 'true'),
(1, 'troco_activo', 'true'),
(1, 'codigo_barras_supervisor', 'SUP001');