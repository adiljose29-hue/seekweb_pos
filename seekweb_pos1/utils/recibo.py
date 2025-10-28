import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from decimal import Decimal

class GeradorRecibos:
    def __init__(self, config):
        self.config = config
        self.local_recibos = config.get('Caixa', 'local_recibos', fallback='recibos/')
        self.setup_diretorio()
    
    def setup_diretorio(self):
        """Cria o diretório de recibos se não existir"""
        if not os.path.exists(self.local_recibos):
            os.makedirs(self.local_recibos)
            print(f"✅ Diretório de recibos criado: {self.local_recibos}")
    
    def gerar_recibo_venda(self, dados_venda, itens, pagamentos, empresa_info):
        """Gera um recibo PDF para a venda"""
        try:
            numero_venda = dados_venda['numero_venda']
            filename = f"{self.local_recibos}recibo_{numero_venda}.pdf"
            
            doc = SimpleDocTemplate(
                filename,
                pagesize=portrait(A4),
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para o recibo
            estilo_titulo = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,  # Centro
                textColor=colors.HexColor('#2c3e50')
            )
            
            estilo_normal = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12
            )
            
            estilo_negrito = ParagraphStyle(
                'CustomBold',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Cabeçalho
            story.append(Paragraph("<b>SEEKWEB COMÉRCIO</b>", estilo_titulo))
            story.append(Paragraph(f"<b>NIF:</b> {empresa_info.get('nif', '5000000000')}", estilo_normal))
            story.append(Paragraph(f"<b>Telefone:</b> {empresa_info.get('telefone', '+244 123 456 789')}", estilo_normal))
            story.append(Paragraph(f"<b>Endereço:</b> {empresa_info.get('endereco', 'Luanda, Angola')}", estilo_normal))
            story.append(Spacer(1, 20))
            
            # Linha separadora
            story.append(Paragraph("<hr/>", estilo_normal))
            story.append(Spacer(1, 20))
            
            # Informações da venda
            story.append(Paragraph(f"<b>RECIBO DE VENDA:</b> {numero_venda}", estilo_negrito))
            story.append(Paragraph(f"<b>Data:</b> {dados_venda['created_at'].strftime('%d/%m/%Y %H:%M')}", estilo_normal))
            story.append(Paragraph(f"<b>Vendedor:</b> {dados_venda.get('vendedor', 'Sistema')}", estilo_normal))
            
            if dados_venda.get('cliente_nome'):
                story.append(Paragraph(f"<b>Cliente:</b> {dados_venda['cliente_nome']}", estilo_normal))
            
            story.append(Spacer(1, 20))
            
            # Tabela de itens
            dados_tabela = [
                ['Produto', 'Qtd', 'Preço Unit.', 'IVA', 'Total']
            ]
            
            for item in itens:
                dados_tabela.append([
                    item['produto_nome'][:30],  # Limitar tamanho do nome
                    str(item['quantidade']),
                    f"{item['preco_unitario']:.2f} Kz",
                    f"{item.get('taxa_iva', 14)}%",
                    f"{item['subtotal']:.2f} Kz"
                ])
            
            tabela = Table(dados_tabela, colWidths=[200, 50, 80, 50, 80])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
            ]))
            
            story.append(tabela)
            story.append(Spacer(1, 20))
            
            # Totais
            story.append(Paragraph(f"<b>Subtotal:</b> {dados_venda['total_sem_iva']:.2f} Kz", estilo_negrito))
            story.append(Paragraph(f"<b>IVA:</b> {dados_venda['total_iva']:.2f} Kz", estilo_negrito))
            story.append(Paragraph(f"<b>TOTAL:</b> {dados_venda['total_com_iva']:.2f} Kz", estilo_negrito))
            story.append(Spacer(1, 20))
            
            # Pagamentos
            if pagamentos:
                story.append(Paragraph("<b>FORMA(S) DE PAGAMENTO:</b>", estilo_negrito))
                for pagamento in pagamentos:
                    story.append(Paragraph(
                        f"- {pagamento['forma_pagamento']}: {pagamento['valor']:.2f} Kz", 
                        estilo_normal
                    ))
                    if pagamento.get('troco', 0) > 0:
                        story.append(Paragraph(
                            f"  Troco: {pagamento['troco']:.2f} Kz", 
                            estilo_normal
                        ))
            
            story.append(Spacer(1, 30))
            
            # Rodapé
            story.append(Paragraph("<hr/>", estilo_normal))
            story.append(Spacer(1, 10))
            story.append(Paragraph("Obrigado pela sua preferência!", estilo_normal))
            story.append(Paragraph("Volte sempre!", estilo_normal))
            
            # Gerar PDF
            doc.build(story)
            print(f"✅ Recibo gerado: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Erro ao gerar recibo: {e}")
            return None

    def gerar_recibo_simplificado(self, dados_venda, itens, pagamentos):
        """Gera um recibo simplificado para impressão térmica"""
        try:
            # Para impressoras térmicas - formato texto simples
            filename = f"{self.local_recibos}recibo_simple_{dados_venda['numero_venda']}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 40 + "\n")
                f.write("      SEEKWEB COMÉRCIO\n")
                f.write("=" * 40 + "\n")
                f.write(f"Recibo: {dados_venda['numero_venda']}\n")
                f.write(f"Data: {dados_venda['created_at'].strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Vendedor: {dados_venda.get('vendedor', 'Sistema')}\n")
                
                if dados_venda.get('cliente_nome'):
                    f.write(f"Cliente: {dados_venda['cliente_nome']}\n")
                
                f.write("-" * 40 + "\n")
                f.write("ITENS:\n")
                
                for item in itens:
                    f.write(f"{item['produto_nome'][:20]:20} ")
                    f.write(f"{item['quantidade']:2} x ")
                    f.write(f"{item['preco_unitario']:6.2f} = ")
                    f.write(f"{item['subtotal']:8.2f}\n")
                
                f.write("-" * 40 + "\n")
                f.write(f"Subtotal: {dados_venda['total_sem_iva']:10.2f} Kz\n")
                f.write(f"IVA:      {dados_venda['total_iva']:10.2f} Kz\n")
                f.write(f"TOTAL:    {dados_venda['total_com_iva']:10.2f} Kz\n")
                f.write("-" * 40 + "\n")
                f.write("PAGAMENTOS:\n")
                
                for pagamento in pagamentos:
                    f.write(f"{pagamento['forma_pagamento']}: {pagamento['valor']:.2f} Kz\n")
                    if pagamento.get('troco', 0) > 0:
                        f.write(f"Troco: {pagamento['troco']:.2f} Kz\n")
                
                f.write("=" * 40 + "\n")
                f.write("Obrigado pela preferência!\n")
                f.write("Volte sempre!\n")
                f.write("=" * 40 + "\n")
            
            print(f"✅ Recibo simplificado gerado: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Erro ao gerar recibo simplificado: {e}")
            return None