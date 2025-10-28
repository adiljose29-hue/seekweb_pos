import serial
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class Scanner(QObject):
    codigo_lido = pyqtSignal(str)  # Sinal emitido quando um código é lido
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.serial_conn = None
        self.leitura_ativa = False
        self.thread_leitura = None
        self.setup_scanner()
    
    def setup_scanner(self):
        """Configura conexão com scanner baseado no tipo"""
        try:
            tipo = self.config.get('Scanner', 'tipo', fallback='usb')
            
            if tipo == 'com':
                porta = self.config.get('Scanner', 'porta_com', fallback='COM1')
                velocidade = self.config.getint('Scanner', 'velocidade', fallback=9600)
                
                print(f"🔌 Tentando conectar scanner na porta {porta}...")
                self.serial_conn = serial.Serial(
                    port=porta,
                    baudrate=velocidade,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1
                )
                print(f"✅ Scanner conectado na porta {porta}")
                
            elif tipo == 'usb':
                print("🔌 Scanner USB - Aguardando leitura via emulação de teclado")
                # Para scanners USB que emulam teclado, não precisa de configuração serial
                
            else:
                print("🔌 Scanner Windows - Usando entrada padrão")
                
        except Exception as e:
            print(f"❌ Erro ao conectar scanner: {e}")
    
    def iniciar_leitura(self):
        """Inicia a leitura contínua do scanner"""
        if self.leitura_ativa:
            return
            
        self.leitura_ativa = True
        
        # Se for scanner COM, inicia thread de leitura
        if self.serial_conn and self.config.get('Scanner', 'tipo') == 'com':
            self.thread_leitura = threading.Thread(target=self._ler_serial_continuo)
            self.thread_leitura.daemon = True
            self.thread_leitura.start()
            print("📡 Iniciando leitura contínua do scanner COM...")
        else:
            print("📡 Scanner pronto para leitura (USB/Teclado)")
    
    def parar_leitura(self):
        """Para a leitura do scanner"""
        self.leitura_ativa = False
        if self.thread_leitura:
            self.thread_leitura.join(timeout=1)
        print("⏹️ Leitura do scanner parada")
    
    def _ler_serial_continuo(self):
        """Lê dados continuamente da porta serial (para scanners COM)"""
        buffer = ""
        while self.leitura_ativa:
            try:
                if self.serial_conn and self.serial_conn.in_waiting:
                    dados = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    
                    for char in dados:
                        if char == '\r' or char == '\n':  # Fim do código
                            if buffer.strip():
                                codigo = buffer.strip()
                                print(f"📦 Código lido: {codigo}")
                                self.codigo_lido.emit(codigo)
                                buffer = ""
                        else:
                            buffer += char
                            
                time.sleep(0.01)  # Pequena pausa para não sobrecarregar
                
            except Exception as e:
                print(f"❌ Erro na leitura serial: {e}")
                time.sleep(1)  # Espera antes de tentar novamente
    
    def simular_leitura_teclado(self, codigo):
        """Simula leitura de código para scanners USB/teclado"""
        if self.leitura_ativa:
            print(f"📦 Código simulado: {codigo}")
            self.codigo_lido.emit(codigo)
    
    def processar_entrada_teclado(self, event):
        """Processa entrada de teclado para capturar códigos de barras"""
        # Esta função será chamada pelo evento de teclado da interface
        if hasattr(event, 'text') and event.text().strip():
            # Para scanners que emulam teclado, geralmente enviam o código rapidamente
            # Podemos acumular caracteres e detectar quando o código completo foi lido
            print(f"Tecla pressionada: {event.text()}")
    
    def fechar(self):
        """Fecha a conexão com o scanner"""
        self.parar_leitura()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("🔌 Conexão serial fechada")