from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os
from datetime import datetime

class ReceiptGenerator:
    def __init__(self, app_path):
        self.base_path = os.path.dirname(app_path) if os.path.isfile(app_path) else app_path
        self.receipts_path = os.path.join(self.base_path, "receipts")
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReceiptTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a237e')  # Dark blue
        ))
        
        # Address style
        self.styles.add(ParagraphStyle(
            name='ReceiptAddress',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#424242'),  # Dark grey
            spaceAfter=5
        ))
        
        # Section Header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a237e'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='ReceiptInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8
        ))
        
        # Amount style
        self.styles.add(ParagraphStyle(
            name='ReceiptAmount',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1b5e20')  # Dark green
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='ReceiptFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        ))

    def generate_receipt(self, payment_data, student_data):
        """Generate a receipt PDF"""
        os.makedirs(self.receipts_path, exist_ok=True)
        filename = f"receipt_{payment_data['receipt_number']}.pdf"
        filepath = os.path.join(self.receipts_path, filename)
        
        # Create PDF with margins
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                              rightMargin=30, leftMargin=30,
                              topMargin=20, bottomMargin=20)
        
        story = []
        
        # Add logo if exists
        logo_path = os.path.join(self.base_path, "assets", "logo.png")
        if os.path.exists(logo_path):
            img = Image(logo_path, width=60*mm, height=30*mm)
            story.append(img)
            story.append(Spacer(1, 10))
        
        # Header
        story.append(Paragraph("IMPACTECH CODING ACADEMY", self.styles['ReceiptTitle']))
        story.append(Paragraph("Suite 4/5, De-West Plaza, Power Plant Road,<br/>Agwa Kaduna", 
                             self.styles['ReceiptAddress']))
        story.append(Paragraph("Phone: 07032196863 | Email: info@impacttech-solutions.com", 
                             self.styles['ReceiptAddress']))
        
        # Add horizontal line
        story.append(Spacer(1, 10))
        story.append(Table([['']], colWidths=[450], 
                         style=[('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#1a237e'))]))
        story.append(Spacer(1, 20))
        
        # Receipt details
        receipt_info = [
            [Paragraph("<b>Receipt Number:</b>", self.styles['ReceiptInfo']),
             Paragraph(str(payment_data['receipt_number']), self.styles['ReceiptInfo'])],
            [Paragraph("<b>Date:</b>", self.styles['ReceiptInfo']),
             Paragraph(payment_data['payment_date'], self.styles['ReceiptInfo'])]
        ]
        
        receipt_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
        receipt_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#424242')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(receipt_table)
        
        # Student details
        story.append(Paragraph("STUDENT INFORMATION", self.styles['SectionHeader']))
        student_info = [
            [Paragraph("<b>Student Name:</b>", self.styles['ReceiptInfo']),
             Paragraph(str(student_data['name']), self.styles['ReceiptInfo'])],
            [Paragraph("<b>Registration Number:</b>", self.styles['ReceiptInfo']),
             Paragraph(str(student_data['reg_number']), self.styles['ReceiptInfo'])],
            [Paragraph("<b>Programme:</b>", self.styles['ReceiptInfo']),
             Paragraph(str(student_data['programme']), self.styles['ReceiptInfo'])]
        ]
        
        student_table = Table(student_info, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#424242')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(student_table)
        
        # Payment details
        story.append(Paragraph("PAYMENT DETAILS", self.styles['SectionHeader']))
        programme_fee = student_data.get('programme_fee', 0)
        total_paid = payment_data.get('total_paid', 0)
        balance = payment_data.get('balance', programme_fee - total_paid)
        
        payment_info = [
            ['Description', 'Amount'],
            ['Programme Fee', f"₦{programme_fee:,.2f}"],
            ['Amount Paid', f"₦{payment_data['amount']:,.2f}"],
            ['Total Amount Paid', f"₦{total_paid:,.2f}"],
            ['Balance', f"₦{balance:,.2f}"]
        ]
        
        payment_table = Table(payment_info, colWidths=[3*inch, 3*inch])
        payment_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#424242')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1a237e')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.gray),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(payment_table)
        
        # Add payment note if exists
        if payment_data.get('payment_note'):
            story.append(Spacer(1, 15))
            story.append(Paragraph("Payment Note:", self.styles['SectionHeader']))
            story.append(Paragraph(payment_data['payment_note'], self.styles['ReceiptInfo']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Thank you for your payment!", self.styles['ReceiptFooter']))
        story.append(Spacer(1, 5))
        story.append(Paragraph("This is a computer-generated receipt and does not require a signature.", 
                             self.styles['ReceiptFooter']))
        
        # Build PDF
        doc.build(story)
        return filepath 