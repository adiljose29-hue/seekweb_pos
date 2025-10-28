import win32print
import win32ui
from PIL import Image, ImageWin
import os

class Impressora:
    def __init__(self, config):
        self.config = config
    
    def imprimir_recibo(self, dados_venda):
        """Imprime recibo da venda"""
        try:
            printer_name = self.config.get('Impressora', 'nome_impressora')
            
            if self.config.get('Impressora', 'tipo') == 'windows':
                self._imprimir_windows(printer_name, dados_venda)
            else:
                self._imprimir_serial(dados_venda)
                
        except Exception as e:
            print(f"Erro ao imprimir: {e}")
    
    def _imprimir_windows(self, printer_name, dados_venda):
        """Imprime usando impressora Windows"""
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            hdc.StartDoc("Recibo SeekWeb")
            hdc.StartPage()
            
            # Configurações de fonte
            font = win32ui.CreateFont({
                "name": "Courier New",
                "height": 12,
            })
            hdc.SelectObject(font)
            
            # Cabeçalho
            empresa = self.config.get('Recibo', 'empresa_nome')
            hdc.TextOut(100, 50, empresa)
            hdc.TextOut(100, 70, "=" * 40)
            
            # Itens da venda
            y = 100
            for item in dados_venda['itens']:
                linha = f"{item['nome'][:20]:20} {item['quantidade']:3} x {item['preco']:8.2f}"
                hdc.TextOut(100, y, linha)
                y += 20
            
            # Total
            hdc.TextOut(100, y + 20, f"TOTAL: {dados_venda['total']:10.2f}")
            
            hdc.EndPage()
            hdc.EndDoc()
            
        finally:
            win32print.ClosePrinter(hprinter)
    
    def _imprimir_serial(self, dados_venda):
        """Imprime via porta serial (para impressoras não-Windows)"""
        # Implementação para impressoras USB/COM
        pass
    
    def cortar_papel(self):
        """Executa corte de papel se suportado"""
        if self.config.getboolean('Impressora', 'corte_papel'):
            # Comando ESC/P para corte de papel
            pass