import sys
import os
import json
import base64
import shutil
from io import BytesIO
from datetime import datetime
from pathlib import Path

import qrcode
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from jinja2 import Template

def resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso / icono para compilacion borrar en caso de no desear"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class QRGeneratorTab(QWidget):
    """Tab para generar QR directamente"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.fecha = QDateEdit(datetime.now().date())
        self.cuit = QLineEdit()
        self.ptoVta = QLineEdit()
        self.tipoCmp = QLineEdit("6")
        self.nroCmp = QLineEdit()
        self.importe = QLineEdit()
        self.moneda = QLineEdit("ARS")
        self.ctz = QLineEdit("1")
        self.tipoDocRec = QLineEdit("80")
        self.nroDocRec = QLineEdit()
        self.tipoCodAut = QLineEdit("E")
        self.codAut = QLineEdit()
        self.btn_generar = QPushButton("Generar QR")
        self.btn_generar.clicked.connect(self.generar_qr)
        

        form_layout.addRow("Fecha:", self.fecha)
        form_layout.addRow("CUIT:", self.cuit)
        form_layout.addRow("Punto de Venta:", self.ptoVta)
        form_layout.addRow("Tipo Comprobante:", self.tipoCmp)
        form_layout.addRow("Número Comprobante:", self.nroCmp)
        form_layout.addRow("Importe:", self.importe)
        form_layout.addRow("Moneda:", self.moneda)
        form_layout.addRow("Cotización:", self.ctz)
        form_layout.addRow("Tipo Doc Receptor:", self.tipoDocRec)
        form_layout.addRow("Número Doc Receptor:", self.nroDocRec)
        form_layout.addRow("Tipo Cód. Autorización:", self.tipoCodAut)
        form_layout.addRow("Código Autorización:", self.codAut)
        form_layout.addRow(self.btn_generar)
        
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        self.qr_label = QLabel()
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("border: 2px solid #ccc; background: white;")
        self.qr_label.setText("QR generado aparecerá aquí")
        
        self.btn_guardar = QPushButton("Guardar QR como PNG")
        self.btn_guardar.clicked.connect(self.guardar_qr)
        self.btn_guardar.setEnabled(False)
        
        preview_layout.addWidget(QLabel("Vista previa:"))
        preview_layout.addWidget(self.qr_label)
        preview_layout.addWidget(self.btn_guardar)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(form_widget)
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        self.current_qr_image = None
    
    def generar_qr(self):
        try:
            qr_data = {
                'ver': 1,
                'fecha': self.fecha.date().toString("yyyy-MM-dd"),
                'cuit': int(self.cuit.text()) if self.cuit.text() else 0,
                'ptoVta': int(self.ptoVta.text()) if self.ptoVta.text() else 0,
                'tipoCmp': int(self.tipoCmp.text()) if self.tipoCmp.text() else 6,
                'nroCmp': int(self.nroCmp.text()) if self.nroCmp.text() else 0,
                'importe': float(self.importe.text()) if self.importe.text() else 0,
                'moneda': self.moneda.text(),
                'ctz': float(self.ctz.text()) if self.ctz.text() else 1,
                'tipoDocRec': int(self.tipoDocRec.text()) if self.tipoDocRec.text() else 80,
                'nroDocRec': int(self.nroDocRec.text()) if self.nroDocRec.text() else 0,
                'tipoCodAut': self.tipoCodAut.text(),
                'codAut': int(self.codAut.text()) if self.codAut.text() else 0
            }
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self.current_qr_image = buffer.getvalue()
            
            pixmap = QPixmap()
            pixmap.loadFromData(self.current_qr_image)
            self.qr_label.setPixmap(
                pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            
            self.btn_guardar.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando QR: {str(e)}")
    
    def guardar_qr(self):
        if self.current_qr_image:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar QR", "qr_generado.png", "PNG Files (*.png)"
            )
            if filename:
                with open(filename, 'wb') as f:
                    f.write(self.current_qr_image)
                QMessageBox.information(self, "Éxito", f"QR guardado en {filename}")


class QuickQRDialog(QDialog):
    """Diálogo simple y rápido para generar QR"""
    def __init__(self, parent=None, suggested_data=None):
        super().__init__(parent)
        self.setWindowTitle("Generar QR")
        self.setModal(True)
        self.qr_image = None
        self.init_ui(suggested_data)
        
    def init_ui(self, suggested_data):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.fecha = QDateEdit(datetime.now().date())
        self.cuit = QLineEdit()
        self.ptoVta = QLineEdit()
        self.tipoCmp = QLineEdit("6")
        self.nroCmp = QLineEdit()
        self.importe = QLineEdit()
        self.moneda = QLineEdit("ARS")
        self.ctz = QLineEdit("1")
        self.tipoDocRec = QLineEdit("80")
        self.nroDocRec = QLineEdit()
        self.tipoCodAut = QLineEdit("E")
        self.codAut = QLineEdit()
        
        if suggested_data:
            if 'fecha' in suggested_data:
                self.fecha.setDate(suggested_data.get('fecha', datetime.now().date()))
            if 'cuit' in suggested_data:
                self.cuit.setText(str(suggested_data.get('cuit', '')))
            if 'ptoVta' in suggested_data:
                self.ptoVta.setText(str(suggested_data.get('ptoVta', '')))
            if 'tipoCmp' in suggested_data:
                self.tipoCmp.setText(str(suggested_data.get('tipoCmp', '6')))
            if 'nroCmp' in suggested_data:
                self.nroCmp.setText(str(suggested_data.get('nroCmp', '')))
            if 'importe' in suggested_data:
                self.importe.setText(str(suggested_data.get('importe', '')))
            if 'nroDocRec' in suggested_data:
                self.nroDocRec.setText(str(suggested_data.get('nroDocRec', '')))
            if 'codAut' in suggested_data:
                self.codAut.setText(str(suggested_data.get('codAut', '')))
        
        form.addRow("Fecha:", self.fecha)
        form.addRow("CUIT:", self.cuit)
        form.addRow("Punto Venta:", self.ptoVta)
        form.addRow("Tipo Comprobante:", self.tipoCmp)
        form.addRow("Número Comprobante:", self.nroCmp)
        form.addRow("Importe:", self.importe)
        form.addRow("Moneda:", self.moneda)
        form.addRow("Cotización:", self.ctz)
        form.addRow("Tipo Doc Receptor:", self.tipoDocRec)
        form.addRow("Número Doc Receptor:", self.nroDocRec)
        form.addRow("Tipo Cód. Autorización:", self.tipoCodAut)
        form.addRow("Código Autorización:", self.codAut)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.generate_and_accept)
        btn_box.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(btn_box)
        self.setLayout(layout)
        
    def generate_and_accept(self):
        try:
            qr_data = {
                'ver': 1,
                'fecha': self.fecha.date().toString("yyyy-MM-dd"),
                'cuit': int(self.cuit.text()) if self.cuit.text() else 0,
                'ptoVta': int(self.ptoVta.text()) if self.ptoVta.text() else 0,
                'tipoCmp': int(self.tipoCmp.text()) if self.tipoCmp.text() else 6,
                'nroCmp': int(self.nroCmp.text()) if self.nroCmp.text() else 0,
                'importe': float(self.importe.text()) if self.importe.text() else 0,
                'moneda': self.moneda.text(),
                'ctz': float(self.ctz.text()) if self.ctz.text() else 1,
                'tipoDocRec': int(self.tipoDocRec.text()) if self.tipoDocRec.text() else 80,
                'nroDocRec': int(self.nroDocRec.text()) if self.nroDocRec.text() else 0,
                'tipoCodAut': self.tipoCodAut.text(),
                'codAut': int(self.codAut.text()) if self.codAut.text() else 0
            }
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self.qr_image = buffer.getvalue()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generando QR: {str(e)}")
    
    def get_qr_image(self):
        return self.qr_image


class FacturaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.qr_image_data = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        business_group = QGroupBox("Datos del Negocio")
        business_layout = QFormLayout()
        
        self.business_name = QLineEdit()
        self.business_address = QLineEdit()
        self.business_vat = QLineEdit()
        self.business_tax_id = QLineEdit()
        self.business_gross_income = QLineEdit()
        self.business_start_date = QDateEdit(datetime.now().date())
        
        business_layout.addRow("Razón Social:", self.business_name)
        business_layout.addRow("Domicilio:", self.business_address)
        business_layout.addRow("Condición IVA:", self.business_vat)
        business_layout.addRow("CUIT:", self.business_tax_id)
        business_layout.addRow("Ingresos Brutos:", self.business_gross_income)
        business_layout.addRow("Inicio Actividades:", self.business_start_date)
        business_group.setLayout(business_layout)
        
        bill_group = QGroupBox("Datos de Factura")
        bill_layout = QFormLayout()
        
        self.bill_type = QLineEdit("A")
        self.bill_point_of_sale = QLineEdit()
        self.bill_number = QLineEdit()
        self.bill_date = QDateEdit(datetime.now().date())
        self.bill_since = QDateEdit(datetime.now().date())
        self.bill_until = QDateEdit(datetime.now().date())
        self.bill_expiration = QDateEdit(datetime.now().date())
        self.bill_cae = QLineEdit()
        self.bill_cae_expiration = QDateEdit(datetime.now().date())
        
        bill_layout.addRow("Tipo (A/B/C):", self.bill_type)
        bill_layout.addRow("Punto Venta:", self.bill_point_of_sale)
        bill_layout.addRow("Número:", self.bill_number)
        bill_layout.addRow("Fecha Emisión:", self.bill_date)
        bill_layout.addRow("Período Desde:", self.bill_since)
        bill_layout.addRow("Período Hasta:", self.bill_until)
        bill_layout.addRow("Vencimiento Pago:", self.bill_expiration)
        bill_layout.addRow("CAE:", self.bill_cae)
        bill_layout.addRow("Vencimiento CAE:", self.bill_cae_expiration)
        bill_group.setLayout(bill_layout)
        
        client_group = QGroupBox("Datos del Cliente")
        client_layout = QFormLayout()
        
        self.client_name = QLineEdit()
        self.client_address = QLineEdit()
        self.client_tax_id = QLineEdit()
        self.client_vat = QLineEdit()
        self.client_payment = QLineEdit("Contado")
        
        client_layout.addRow("Nombre/Razón Social:", self.client_name)
        client_layout.addRow("Domicilio:", self.client_address)
        client_layout.addRow("CUIT/CUIL:", self.client_tax_id)
        client_layout.addRow("Condición IVA:", self.client_vat)
        client_layout.addRow("Condición Venta:", self.client_payment)
        client_group.setLayout(client_layout)
        
        items_group = QGroupBox("Ítems")
        items_layout = QVBoxLayout()
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        
        self.btn_add_item = QPushButton("+ Agregar Ítem")
        self.btn_add_item.clicked.connect(self.add_item_row)
        
        items_layout.addWidget(self.items_widget)
        items_layout.addWidget(self.btn_add_item)
        items_group.setLayout(items_layout)
        
        totals_group = QGroupBox("Totales")
        totals_layout = QFormLayout()
        
        self.total_subtotal = QLineEdit()
        self.total_tax = QLineEdit()
        self.total_total = QLineEdit()
        
        totals_layout.addRow("Subtotal:", self.total_subtotal)
        totals_layout.addRow("Impuestos:", self.total_tax)
        totals_layout.addRow("Total:", self.total_total)
        totals_group.setLayout(totals_layout)
        
        qr_group = QGroupBox("Código QR")
        qr_layout = QVBoxLayout()
        
        qr_options_layout = QHBoxLayout()
        self.btn_generate_qr = QPushButton("Generar QR")
        self.btn_load_qr = QPushButton("Cargar QR")
        self.btn_clear_qr = QPushButton("Eliminar QR")
        
        self.btn_generate_qr.clicked.connect(self.generate_qr_for_invoice)
        self.btn_load_qr.clicked.connect(self.load_qr_image)
        self.btn_clear_qr.clicked.connect(self.clear_qr)
        
        qr_options_layout.addWidget(self.btn_generate_qr)
        qr_options_layout.addWidget(self.btn_load_qr)
        qr_options_layout.addWidget(self.btn_clear_qr)
        
        self.qr_preview = QLabel("Sin QR")
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setMinimumSize(100, 100)
        self.qr_preview.setMaximumSize(100, 100)
        self.qr_preview.setStyleSheet("border: 1px solid #ccc; background: white;")
        
        qr_layout.addLayout(qr_options_layout)
        qr_layout.addWidget(QLabel("Vista previa:"))
        qr_layout.addWidget(self.qr_preview)
        qr_group.setLayout(qr_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Generar Factura HTML")
        self.btn_generate.clicked.connect(self.generate_invoice)
        
        buttons_layout.addWidget(self.btn_generate)
        buttons_layout.addStretch()
        
        layout.addWidget(business_group)
        layout.addWidget(bill_group)
        layout.addWidget(client_group)
        layout.addWidget(items_group)
        layout.addWidget(totals_group)
        layout.addWidget(qr_group)
        layout.addLayout(buttons_layout)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        self.add_item_row()
    
    def generate_qr_for_invoice(self):
        """Genera QR con diálogo rápido"""
        dialog = QuickQRDialog(self, {
            'fecha': self.bill_date.date(),
            'cuit': self.business_tax_id.text(),
            'ptoVta': self.bill_point_of_sale.text(),
            'tipoCmp': '1' if self.bill_type.text() == 'A' else '6',
            'nroCmp': self.bill_number.text(),
            'importe': self.total_total.text(),
            'nroDocRec': self.client_tax_id.text(),
            'codAut': self.bill_cae.text()
        })
        
        if dialog.exec():
            self.qr_image_data = dialog.get_qr_image()
            if self.qr_image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(self.qr_image_data)
                self.qr_preview.setPixmap(
                    pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
    
    def load_qr_image(self):
        """Carga una imagen de QR desde archivo"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen QR", "", "PNG Files (*.png);;All Files (*)"
        )
        if filename:
            with open(filename, 'rb') as f:
                self.qr_image_data = f.read()
            
            pixmap = QPixmap(filename)
            self.qr_preview.setPixmap(
                pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
    
    def clear_qr(self):
        """Elimina el QR cargado/generado"""
        self.qr_image_data = None
        self.qr_preview.setText("Sin QR")
        self.qr_preview.setPixmap(QPixmap())
    
    def add_item_row(self):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        
        code = QLineEdit()
        code.setPlaceholderText("Código")
        name = QLineEdit()
        name.setPlaceholderText("Descripción")
        qty = QLineEdit()
        qty.setPlaceholderText("Cant.")
        unit = QLineEdit()
        unit.setPlaceholderText("Unidad")
        price = QLineEdit()
        price.setPlaceholderText("Precio")
        discount = QLineEdit()
        discount.setPlaceholderText("Desc. %")
        discount_val = QLineEdit()
        discount_val.setPlaceholderText("Desc. $")
        subtotal = QLineEdit()
        subtotal.setPlaceholderText("Subtotal")
        
        btn_remove = QPushButton("X")
        btn_remove.clicked.connect(lambda: self.remove_item(item_widget))
        
        for widget in [code, name, qty, unit, price, discount, discount_val, subtotal, btn_remove]:
            widget.setMaximumWidth(80)
            item_layout.addWidget(widget)
        
        self.items_layout.addWidget(item_widget)
    
    def remove_item(self, widget):
        widget.deleteLater()
    
    def generate_invoice(self):
        """Genera la factura HTML"""
        if not self.qr_image_data:
            reply = QMessageBox.question(
                self, "Sin QR",
                "No se ha generado o cargado un QR. ¿Desea generar uno automáticamente?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    qr_data = {
                        'ver': 1,
                        'fecha': self.bill_date.date().toString("yyyy-MM-dd"),
                        'cuit': int(self.business_tax_id.text()) if self.business_tax_id.text() else 0,
                        'ptoVta': int(self.bill_point_of_sale.text()) if self.bill_point_of_sale.text() else 0,
                        'tipoCmp': 1 if self.bill_type.text() == 'A' else 6,
                        'nroCmp': int(self.bill_number.text()) if self.bill_number.text() else 0,
                        'importe': float(self.total_total.text()) if self.total_total.text() else 0,
                        'moneda': 'ARS',
                        'ctz': 1,
                        'tipoDocRec': 80,
                        'nroDocRec': int(self.client_tax_id.text()) if self.client_tax_id.text() else 0,
                        'tipoCodAut': 'E',
                        'codAut': int(self.bill_cae.text()) if self.bill_cae.text() else 0
                    }
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(json.dumps(qr_data))
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    self.qr_image_data = buffer.getvalue()
                    
                    pixmap = QPixmap()
                    pixmap.loadFromData(self.qr_image_data)
                    self.qr_preview.setPixmap(
                        pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error generando QR automático: {str(e)}")
            else:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data("Sin datos")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                self.qr_image_data = buffer.getvalue()
        
        reply = QMessageBox.question(
            self, "Guardar archivos",
            "¿Desea guardar los archivos en una carpeta?\n\n"
            "Sí: Crear carpeta con HTML y QR PNG\n"
            "No: Guardar solo HTML con QR embebido",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            return
        
        business_data = {
            'business_name': self.business_name.text() or "EMPRESA S.A.",
            'address': self.business_address.text() or "Calle 123, Ciudad",
            'vat_condition': self.business_vat.text() or "Responsable Inscripto",
            'tax_id': self.business_tax_id.text() or "30-12345678-9",
            'gross_income_id': self.business_gross_income.text() or "123-456789-0",
            'start_date': self.business_start_date.date().toString("yyyy-MM-dd")
        }
        
        bill_data = {
            'type': self.bill_type.text() or "A",
            'point_of_sale': self.bill_point_of_sale.text() or "0001",
            'number': self.bill_number.text() or "00001234",
            'date': self.bill_date.date().toString("yyyy-MM-dd"),
            'since': self.bill_since.date().toString("yyyy-MM-dd"),
            'until': self.bill_until.date().toString("yyyy-MM-dd"),
            'expiration': self.bill_expiration.date().toString("yyyy-MM-dd"),
            'CAE': self.bill_cae.text() or "12345678901234",
            'CAE_expiration': self.bill_cae_expiration.date().toString("yyyy-MM-dd")
        }
        
        billing_data = {
            'name': self.client_name.text() or "Cliente S.A.",
            'address': self.client_address.text() or "Calle 456, Ciudad",
            'tax_id': self.client_tax_id.text() or "30-98765432-1",
            'vat_condition': self.client_vat.text() or "Responsable Inscripto",
            'payment_method': self.client_payment.text() or "Contado"
        }
        
        items = []
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                children = widget.findChildren(QLineEdit)
                if len(children) >= 9:
                    items.append({
                        'code': children[0].text() or "001",
                        'name': children[1].text() or "Producto",
                        'quantity': children[2].text() or "1",
                        'measurement_unit': children[3].text() or "unidad",
                        'price': children[4].text() or "100.00",
                        'percent_subsidized': children[5].text() or "0",
                        'impost_subsidized': children[6].text() or "0.00",
                        'subtotal': children[7].text() or "100.00"
                    })
        
        if not items:
            items.append({
                'code': "001",
                'name': "Producto/Servicio",
                'quantity': "1",
                'measurement_unit': "unidad",
                'price': "100.00",
                'percent_subsidized': "0",
                'impost_subsidized': "0.00",
                'subtotal': "100.00"
            })
        
        overall = {
            'subtotal': self.total_subtotal.text() or "100.00",
            'impost_tax': self.total_tax.text() or "21.00",
            'total': self.total_total.text() or "121.00"
        }
        
        if reply == QMessageBox.Yes:
            folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para guardar")
            if folder:
                folder_path = Path(folder) / f"factura_{bill_data['number']}"
                folder_path.mkdir(exist_ok=True)
                
                qr_filename = folder_path / "qr_code.png"
                with open(qr_filename, 'wb') as f:
                    f.write(self.qr_image_data)
                
                template_str = self.get_factura_template()
                template = Template(template_str)
                html_content = template.render(
                    business_data=business_data,
                    bill=bill_data,
                    billing_data=billing_data,
                    items=items,
                    overall=overall,
                    qr_code_image="qr_code.png"
                )
                
                html_filename = folder_path / "factura.html"
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                QMessageBox.information(
                    self, "Éxito", 
                    f"Archivos guardados en:\n{folder_path}\n\n"
                    f"• factura.html\n• qr_code.png"
                )
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Factura HTML", f"factura_{bill_data['number']}.html", "HTML Files (*.html)"
            )
            if filename:
                qr_base64 = base64.b64encode(self.qr_image_data).decode()
                
                template_str = self.get_factura_template()
                template = Template(template_str)
                html_content = template.render(
                    business_data=business_data,
                    bill=bill_data,
                    billing_data=billing_data,
                    items=items,
                    overall=overall,
                    qr_code_image=f"data:image/png;base64,{qr_base64}"
                )
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                QMessageBox.information(self, "Éxito", f"Factura HTML guardada en:\n{filename}")
    
    def get_factura_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Factura</title>
    <style type="text/css">
        * {
            box-sizing: border-box;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }

        .bill-container {
            width: 750px;
            position: absolute;
            left: 0;
            right: 0;
            margin: auto;
            border-collapse: collapse;
            font-family: sans-serif;
            font-size: 13px;
        }

        .bill-emitter-row td {
            width: 50%;
            border-bottom: 1px solid;
            padding-top: 10px;
            padding-left: 10px;
            vertical-align: top;
        }

        .bill-emitter-row {
            position: relative;
        }

        .bill-emitter-row td:nth-child(2) {
            padding-left: 60px;
        }

        .bill-emitter-row td:nth-child(1) {
            padding-right: 60px;
        }

        .bill-type {
            border: 1px solid;
            border-top: 1px solid;
            border-bottom: 1px solid;
            margin-right: -30px;
            background: white;
            width: 60px;
            height: 50px;
            position: absolute;
            left: 0;
            right: 0;
            top: -1px;
            margin: auto;
            text-align: center;
            font-size: 40px;
            font-weight: 600;
        }

        .text-lg {
            font-size: 30px;
        }

        .text-center {
            text-align: center;
        }

        .col-2 {
            width: 16.66666667%;
            float: left;
        }

        .col-3 {
            width: 25%;
            float: left;
        }

        .col-4 {
            width: 33.3333333%;
            float: left;
        }

        .col-5 {
            width: 41.66666667%;
            float: left;
        }

        .col-6 {
            width: 50%;
            float: left;
        }

        .col-8 {
            width: 66.66666667%;
            float: left;
        }

        .col-10 {
            width: 83.33333333%;
            float: left;
        }

        .row {
            overflow: hidden;
        }

        .margin-b-0 {
            margin-bottom: 0px;
        }

        .bill-row td {
            padding-top: 5px
        }

        .bill-row td>div {
            border-top: 1px solid;
            border-bottom: 1px solid;
            margin: 0 -1px 0 -2px;
            padding: 0 10px 13px 10px;
        }

        .row-details table {
            border-collapse: collapse;
            width: 100%;
        }

        .row-details td>div,
        .row-qrcode td>div {
            border: 0;
            margin: 0 -1px 0 -2px;
            padding: 0;
        }

        .row-details table td {
            padding: 5px;
        }

        .row-details table tr:nth-child(1) {
            border-top: 1px solid;
            border-bottom: 1px solid;
            background: #c0c0c0;
            font-weight: bold;
            text-align: center;
        }

        .row-details table tr+tr {
            border-top: 1px solid #c0c0c0;

        }

        .text-right {
            text-align: right;
        }

        .margin-b-10 {
            margin-bottom: 10px;
        }

        .total-row td>div {
            border-width: 2px;
        }

        .row-qrcode td {
            padding: 10px;
        }

        #qrcode {
            width: 50%
        }
    </style>
</head>

<body>
    <table class="bill-container">
        <tr class="bill-emitter-row">
            <td>
                <div class="bill-type">
                    {{ bill['type'] }}
                </div>
                <div class="text-lg text-center">
                    {{ business_data['business_name'] }}
                </div>
                <p><strong>Razón social:</strong> {{ business_data['business_name'] }}</p>
                <p><strong>Domicilio Comercial:</strong> {{ business_data['address'] }}</p>
                <p><strong>Condición Frente al IVA:</strong> {{ business_data['vat_condition'] }}</p>
            </td>
            <td>
                <div>
                    <div class="text-lg">
                        Factura
                    </div>
                    <div class="row">
                        <p class="col-6 margin-b-0">
                            <strong>Punto de Venta: {{ bill['point_of_sale'] }}</strong>
                        </p>
                        <p class="col-6 margin-b-0">
                            <strong>Comp. Nro: {{ bill['number'] }} </strong>
                        </p>
                    </div>
                    <p><strong>Fecha de Emisión:</strong> {{ bill['date'] }}</p>
                    <p><strong>CUIT:</strong> {{ business_data['tax_id'] }}</p>
                    <p><strong>Ingresos Brutos:</strong> {{ business_data['gross_income_id'] }}</p>
                    <p><strong>Fecha de Inicio de Actividades:</strong> {{ business_data['start_date'] }}</p>
                </div>
            </td>
        </tr>
        <tr class="bill-row">
            <td colspan="2">
                <div class="row">
                    <p class="col-4 margin-b-0">
                        <strong>Período Facturado Desde: </strong>{{ bill['since'] }}
                    </p>
                    <p class="col-3 margin-b-0">
                        <strong>Hasta: </strong>{{ bill['until'] }}
                    </p>
                    <p class="col-5 margin-b-0">
                        <strong>Fecha de Vto. para el pago: </strong>{{ bill['expiration'] }}
                    </p>
                </div>
            </td>
        </tr>
        <tr class="bill-row">
            <td colspan="2">
                <div>
                    <div class="row">
                        <p class="col-4 margin-b-0">
                            <strong>CUIL/CUIT: </strong>{{ billing_data['tax_id'] }}
                        </p>
                        <p class="col-8 margin-b-0">
                            <strong>Apellido y Nombre / Razón social: </strong>{{ billing_data['name'] }}
                        </p>
                    </div>
                    <div class="row">
                        <p class="col-6 margin-b-0">
                            <strong>Condición Frente al IVA: </strong>{{ billing_data['vat_condition'] }}
                        </p>
                        <p class="col-6 margin-b-0">
                            <strong>Domicilio: </strong>{{ billing_data['address'] }}
                        </p>
                    </div>
                    <p>
                        <strong>Condicion de venta: </strong>{{ billing_data['payment_method'] }}
                    </p>
                </div>
            </td>
        </tr>
        <tr class="bill-row row-details">
            <td colspan="2">
                <div>
                    <table>
                        <tr>
                            <td>Código</td>
                            <td>Producto / Servicio</td>
                            <td>Cantidad</td>
                            <td>U. Medida</td>
                            <td>Precio Unit.</td>
                            <td>% Bonif.</td>
                            <td>Imp. Bonif.</td>
                            <td>Subtotal</td>
                        </tr>
                        {% for item in items %}
                        <tr>
                            <td>{{ item['code'] }}</td>
                            <td>{{ item['name'] }}</td>
                            <td>{{ item['quantity'] }}</td>
                            <td>{{ item['measurement_unit'] }}</td>
                            <td>{{ item['price'] }}</td>
                            <td>{{ item['percent_subsidized'] }}</td>
                            <td>{{ item['impost_subsidized'] }}</td>
                            <td>{{ item['subtotal'] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </td>
        </tr>
        <tr class="bill-row total-row">
            <td colspan="2">
                <div>
                    <div class="row text-right">
                        <p class="col-10 margin-b-0">
                            <strong>Subtotal: $</strong>
                        </p>
                        <p class="col-2 margin-b-0">
                            <strong>{{ overall['subtotal'] }}</strong>
                        </p>
                    </div>
                    <div class="row text-right">
                        <p class="col-10 margin-b-0">
                            <strong>Importe Otros Tributos: $</strong>
                        </p>
                        <p class="col-2 margin-b-0">
                            <strong>{{ overall['impost_tax'] }}</strong>
                        </p>
                    </div>
                    <div class="row text-right">
                        <p class="col-10 margin-b-0">
                            <strong>Importe total: $</strong>
                        </p>
                        <p class="col-2 margin-b-0">
                            <strong>{{ overall['total'] }}</strong>
                        </p>
                    </div>
                </div>
            </td>
        </tr>
        <tr class="bill-row row-details">
            <td>
                <div>
                    <div class="row">
                        <img id="qrcode" src="{{ qr_code_image }}">
                    </div>
                </div>
            </td>
            <td>
                <div>
                    <div class="row text-right margin-b-10">
                        <strong>CAE Nº:&nbsp;</strong> {{ bill['CAE'] }}
                    </div>
                    <div class="row text-right">
                        <strong>Fecha de Vto. de CAE:&nbsp;</strong> {{ bill['CAE_expiration'] }}
                    </div>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>"""


class TicketTab(QWidget):
    def __init__(self):
        super().__init__()
        self.qr_image_data = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        business_group = QGroupBox("Datos del Negocio")
        business_layout = QFormLayout()
        
        self.ticket_business_name = QLineEdit()
        self.ticket_business_address = QLineEdit()
        self.ticket_business_tax_id = QLineEdit()
        self.ticket_business_vat = QLineEdit()
        self.ticket_business_gross_income = QLineEdit()
        self.ticket_business_start_date = QDateEdit(datetime.now().date())
        
        business_layout.addRow("Razón Social:", self.ticket_business_name)
        business_layout.addRow("Dirección:", self.ticket_business_address)
        business_layout.addRow("CUIT:", self.ticket_business_tax_id)
        business_layout.addRow("Condición IVA:", self.ticket_business_vat)
        business_layout.addRow("Ingresos Brutos:", self.ticket_business_gross_income)
        business_layout.addRow("Inicio Actividades:", self.ticket_business_start_date)
        business_group.setLayout(business_layout)
        
        ticket_group = QGroupBox("Datos del Ticket")
        ticket_layout = QFormLayout()
        
        self.ticket_type = QLineEdit("A")
        self.ticket_code = QLineEdit()
        self.ticket_point_of_sale = QLineEdit()
        self.ticket_number = QLineEdit()
        self.ticket_date = QDateEdit(datetime.now().date())
        self.ticket_concept = QLineEdit("Venta de productos")
        self.ticket_cae = QLineEdit()
        self.ticket_cae_expiration = QDateEdit(datetime.now().date())
        
        ticket_layout.addRow("Tipo Factura:", self.ticket_type)
        ticket_layout.addRow("Código:", self.ticket_code)
        ticket_layout.addRow("Punto Venta:", self.ticket_point_of_sale)
        ticket_layout.addRow("Número:", self.ticket_number)
        ticket_layout.addRow("Fecha:", self.ticket_date)
        ticket_layout.addRow("Concepto:", self.ticket_concept)
        ticket_layout.addRow("CAE:", self.ticket_cae)
        ticket_layout.addRow("Vencimiento CAE:", self.ticket_cae_expiration)
        ticket_group.setLayout(ticket_layout)
        
        client_group = QGroupBox("Datos del Cliente")
        client_layout = QFormLayout()
        
        self.ticket_client_vat = QLineEdit("Consumidor Final")
        client_layout.addRow("Condición IVA Cliente:", self.ticket_client_vat)
        client_group.setLayout(client_layout)
        
        items_group = QGroupBox("Ítems del Ticket")
        items_layout = QVBoxLayout()
        self.ticket_items_widget = QWidget()
        self.ticket_items_layout = QVBoxLayout(self.ticket_items_widget)
        
        self.btn_add_ticket_item = QPushButton("+ Agregar Ítem")
        self.btn_add_ticket_item.clicked.connect(self.add_ticket_item)
        
        items_layout.addWidget(self.ticket_items_widget)
        items_layout.addWidget(self.btn_add_ticket_item)
        items_group.setLayout(items_layout)
        
        totals_group = QGroupBox("Totales")
        totals_layout = QFormLayout()
        self.ticket_total = QLineEdit()
        totals_layout.addRow("Total:", self.ticket_total)
        totals_group.setLayout(totals_layout)
        
        qr_group = QGroupBox("Código QR")
        qr_layout = QVBoxLayout()
        
        qr_options_layout = QHBoxLayout()
        self.btn_generate_qr = QPushButton("Generar QR")
        self.btn_load_qr = QPushButton("Cargar QR")
        self.btn_clear_qr = QPushButton("Eliminar QR")
        
        self.btn_generate_qr.clicked.connect(self.generate_qr_for_ticket)
        self.btn_load_qr.clicked.connect(self.load_qr_image)
        self.btn_clear_qr.clicked.connect(self.clear_qr)
        
        qr_options_layout.addWidget(self.btn_generate_qr)
        qr_options_layout.addWidget(self.btn_load_qr)
        qr_options_layout.addWidget(self.btn_clear_qr)
        
        self.qr_preview = QLabel("Sin QR")
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setMinimumSize(100, 100)
        self.qr_preview.setMaximumSize(100, 100)
        self.qr_preview.setStyleSheet("border: 1px solid #ccc; background: white;")
        
        qr_layout.addLayout(qr_options_layout)
        qr_layout.addWidget(QLabel("Vista previa:"))
        qr_layout.addWidget(self.qr_preview)
        qr_group.setLayout(qr_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Generar Ticket HTML")
        self.btn_generate.clicked.connect(self.generate_ticket)
        
        buttons_layout.addWidget(self.btn_generate)
        buttons_layout.addStretch()
        
        layout.addWidget(business_group)
        layout.addWidget(ticket_group)
        layout.addWidget(client_group)
        layout.addWidget(items_group)
        layout.addWidget(totals_group)
        layout.addWidget(qr_group)
        layout.addLayout(buttons_layout)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        self.add_ticket_item()
    
    def generate_qr_for_ticket(self):
        """Genera QR con diálogo rápido"""
        dialog = QuickQRDialog(self, {
            'fecha': self.ticket_date.date(),
            'cuit': self.ticket_business_tax_id.text(),
            'ptoVta': self.ticket_point_of_sale.text(),
            'tipoCmp': '1' if self.ticket_type.text() == 'A' else '6',
            'nroCmp': self.ticket_number.text(),
            'importe': self.ticket_total.text(),
            'nroDocRec': 0,
            'codAut': self.ticket_cae.text()
        })
        
        if dialog.exec():
            self.qr_image_data = dialog.get_qr_image()
            if self.qr_image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(self.qr_image_data)
                self.qr_preview.setPixmap(
                    pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
    
    def load_qr_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen QR", "", "PNG Files (*.png);;All Files (*)"
        )
        if filename:
            with open(filename, 'rb') as f:
                self.qr_image_data = f.read()
            
            pixmap = QPixmap(filename)
            self.qr_preview.setPixmap(
                pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
    
    def clear_qr(self):
        self.qr_image_data = None
        self.qr_preview.setText("Sin QR")
        self.qr_preview.setPixmap(QPixmap())
    
    def add_ticket_item(self):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        
        qty = QLineEdit()
        qty.setPlaceholderText("Cant.")
        name = QLineEdit()
        name.setPlaceholderText("Producto")
        tax = QLineEdit()
        tax.setPlaceholderText("IVA %")
        price = QLineEdit()
        price.setPlaceholderText("Precio")
        
        btn_remove = QPushButton("X")
        btn_remove.clicked.connect(lambda: self.remove_ticket_item(item_widget))
        
        for widget in [qty, name, tax, price, btn_remove]:
            widget.setMaximumWidth(100)
            item_layout.addWidget(widget)
        
        self.ticket_items_layout.addWidget(item_widget)
    
    def remove_ticket_item(self, widget):
        widget.deleteLater()
    
    def generate_ticket(self):
        """Genera el ticket HTML"""
        if not self.qr_image_data:
            reply = QMessageBox.question(
                self, "Sin QR",
                "No se ha generado o cargado un QR. ¿Desea generar uno automáticamente?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    qr_data = {
                        'ver': 1,
                        'fecha': self.ticket_date.date().toString("yyyy-MM-dd"),
                        'cuit': int(self.ticket_business_tax_id.text()) if self.ticket_business_tax_id.text() else 0,
                        'ptoVta': int(self.ticket_point_of_sale.text()) if self.ticket_point_of_sale.text() else 0,
                        'tipoCmp': 1 if self.ticket_type.text() == 'A' else 6,
                        'nroCmp': int(self.ticket_number.text()) if self.ticket_number.text() else 0,
                        'importe': float(self.ticket_total.text()) if self.ticket_total.text() else 0,
                        'moneda': 'ARS',
                        'ctz': 1,
                        'tipoDocRec': 99,
                        'nroDocRec': 0,
                        'tipoCodAut': 'E',
                        'codAut': int(self.ticket_cae.text()) if self.ticket_cae.text() else 0
                    }
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(json.dumps(qr_data))
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    self.qr_image_data = buffer.getvalue()
                    
                    pixmap = QPixmap()
                    pixmap.loadFromData(self.qr_image_data)
                    self.qr_preview.setPixmap(
                        pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error generando QR automático: {str(e)}")
            else:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data("Sin datos")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                self.qr_image_data = buffer.getvalue()
        
        reply = QMessageBox.question(
            self, "Guardar archivos",
            "¿Desea guardar los archivos en una carpeta?\n\n"
            "Sí: Crear carpeta con HTML y QR PNG\n"
            "No: Guardar solo HTML con QR embebido",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            return
        
        business_data = {
            'business_name': self.ticket_business_name.text() or "EMPRESA S.A.",
            'address': self.ticket_business_address.text() or "Calle 123, Ciudad",
            'tax_id': self.ticket_business_tax_id.text() or "30-12345678-9",
            'vat_condition': self.ticket_business_vat.text() or "Responsable Inscripto",
            'gross_income_id': self.ticket_business_gross_income.text() or "123-456789-0",
            'start_date': self.ticket_business_start_date.date().toString("yyyy-MM-dd")
        }
        
        bill_data = {
            'type': self.ticket_type.text() or "A",
            'code': self.ticket_code.text() or "COD001",
            'point_of_sale': self.ticket_point_of_sale.text() or "0001",
            'number': self.ticket_number.text() or "00001234",
            'date': self.ticket_date.date().toString("yyyy-MM-dd"),
            'concept': self.ticket_concept.text() or "Venta de productos",
            'CAE': self.ticket_cae.text() or "12345678901234",
            'CAE_expiration': self.ticket_cae_expiration.date().toString("yyyy-MM-dd")
        }
        
        billing_data = {
            'vat_condition': self.ticket_client_vat.text() or "Consumidor Final"
        }
        
        items = []
        for i in range(self.ticket_items_layout.count()):
            widget = self.ticket_items_layout.itemAt(i).widget()
            if widget:
                children = widget.findChildren(QLineEdit)
                if len(children) >= 4:
                    items.append({
                        'quantity': children[0].text() or "1",
                        'name': children[1].text() or "Producto",
                        'tax_percent': children[2].text() or "21",
                        'price': children[3].text() or "100.00"
                    })
        
        if not items:
            items.append({
                'quantity': "1",
                'name': "Producto",
                'tax_percent': "21",
                'price': "100.00"
            })
        
        overall = {
            'total': self.ticket_total.text() or "121.00"
        }
        
        if reply == QMessageBox.Yes:
            folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para guardar")
            if folder:
                folder_path = Path(folder) / f"ticket_{bill_data['number']}"
                folder_path.mkdir(exist_ok=True)
                
                qr_filename = folder_path / "qr_code.png"
                with open(qr_filename, 'wb') as f:
                    f.write(self.qr_image_data)
                
                template_str = self.get_ticket_template()
                template = Template(template_str)
                html_content = template.render(
                    business_data=business_data,
                    bill=bill_data,
                    billing_data=billing_data,
                    items=items,
                    overall=overall,
                    qr_code_image="qr_code.png" 
                )
                
                html_filename = folder_path / "ticket.html"
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                QMessageBox.information(
                    self, "Éxito", 
                    f"Archivos guardados en:\n{folder_path}\n\n"
                    f"• ticket.html\n• qr_code.png"
                )
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Ticket HTML", f"ticket_{bill_data['number']}.html", "HTML Files (*.html)"
            )
            if filename:
                qr_base64 = base64.b64encode(self.qr_image_data).decode()
                
                template_str = self.get_ticket_template()
                template = Template(template_str)
                html_content = template.render(
                    business_data=business_data,
                    bill=bill_data,
                    billing_data=billing_data,
                    items=items,
                    overall=overall,
                    qr_code_image=f"data:image/png;base64,{qr_base64}"
                )
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                QMessageBox.information(self, "Éxito", f"Ticket HTML guardada en:\n{filename}")
    
    def get_ticket_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Ticket</title>
    <style type="text/css">
        *{
            box-sizing: border-box;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }

        .bill-container{
            border-collapse: collapse;
            max-width: 8cm;
            position: absolute;
            left:0;
            right: 0;
            margin: auto;
            border-collapse: collapse;
            font-family: monospace;
            font-size: 12px;
        }

        .text-lg{
            font-size: 20px;
        }

        .text-center{
            text-align: center;
        }
    

        #qrcode {
            width: 75%
        }

        p {
            margin: 2px 0;
        }

        table table {
            width: 100%;
        }

        
        table table tr td:last-child{
            text-align: right;
        }

        .border-top {
            border-top: 1px dashed;
        }

        .padding-b-3 {
            padding-bottom: 3px;
        }

        .padding-t-3 {
            padding-top: 3px;
        }

    </style>
</head>
<body>
    <table class="bill-container">
        <tr>
            <td class="padding-b-3">
                <p>Razón social: {{ business_data['business_name'] }}</p>
                <p>Direccion: {{ business_data['address'] }}</p>
                <p>C.U.I.T.: {{ business_data['tax_id'] }}</p>
                <p>{{ business_data['vat_condition'] }}</p>
                <p>IIBB: {{ business_data['gross_income_id'] }}</p>
                <p>Inicio de actividad: {{ business_data['start_date'] }}</p>
            </td>
        </tr>
        <tr>
            <td class="border-top padding-t-3 padding-b-3">
                <p class="text-center text-lg">FACTURA {{ bill['type'] }}</p>
                <p class="text-center">Codigo {{ bill['code'] }}</p>
                <p>P.V: {{ bill['point_of_sale'] }}</p>
                <p>Nro: {{ bill['number'] }}</p>
                <p>Fecha: {{ bill['date'] }}</p>
                <p>Concepto: {{ bill['concept'] }}</p>
            </td>
        </tr>
        <tr>
            <td class="border-top padding-t-3 padding-b-3">
                <p>A {{ billing_data['vat_condition'] }}</p>
            </td>
        </tr>
        <tr>
            <td class="border-top padding-t-3 padding-b-3">
                <div>
                    <table>
                        {% for item in items %}
                            <tr>
                                <td>{{ item['quantity'] }}</td>
                                <td>{{ item['name'] }}</td>
                                <td>{{ item['tax_percent'] }}</td>
                                <td>{{ item['price'] }}</td>
                            </tr>
                        {% endfor %}
                    </table>
                </div>
            </td>
        </tr>
        <tr>
            <td class="border-top padding-t-3 padding-b-3">
                <div>
                    <table>
                        <tr>
                            <td>TOTAL</td>
                            <td>{{ overall['total'] }}</td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
        <tr>
            <td class="border-top padding-t-3">
                <p>CAE: {{ bill['CAE'] }}</p>
                <p>Vto: {{ bill['CAE_expiration'] }}</p>
            </td>
        </tr>
        <tr class="text-center">
            <td>
                <img id="qrcode" src="{{ qr_code_image }}">
            </td>
        </tr>
    </table>
</body>
</html>"""


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        about_text = """
      <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 25px;  margin: 20px;">
    
    <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #3498db; padding-bottom: 20px;">
        <h1 style=" margin-bottom: 10px; font-weight: 300;">ArcaLinux - Desktop</h1>
        
        <h3 style=" font-weight: normal;">Herramienta de generación de documentos fiscales</h3>
        <hr>
    </div>
    
    <div style="padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #3498db;">
        <p style="margin: 5px 0;"><strong>Version:</strong>1.1.0</p>
    </div>
    
    <div style="margin-bottom: 25px;">
        <h3 style=" border-bottom: 1px solid #4a6572; padding-bottom: 8px; font-weight: 400;">Descripción</h3>
        <p style=" text-align: justify; ">
            Herramienta completa para generación de documentos fiscales con todas las herramientas embebidas necesarias 
            para automatización. Diseñada específicamente para el mercado argentino, cumple con los requisitos de Arca 
            para códigos QR, facturas y tickets.
        </p>
        <p style="line-height: 1.6; text-align: center; padding: 12px; border-radius: 5px; border-left: 4px solid #ffc107; margin-top: 15px; background-color: rgba(255, 195, 7, 0.1);">
             Todas las dependencias están incluidas - no requiere instalación adicional.
        </p>
    </div>
    
   
    
    <div style="margin-bottom: 25px;">
        <h3 style=" border-bottom: 1px solid #4a6572; padding-bottom: 8px; font-weight: 400;">Guía Rápida de Uso</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
            <div style="flex: 1; min-width: 200px; padding: 15px; border-radius: 6px; border: 1px solid #4a6572;">
                <h4 style=" margin-top: 0; font-weight: 400;">1. QR de Arca</h4>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li>Completa los datos del formulario</li>
                    <li>Genera el código QR</li>
                    <li>Guarda como imagen PNG</li>
                </ol>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 15px; border-radius: 6px; border: 1px solid #4a6572;">
                <h4 style=" margin-top: 0; font-weight: 400;">2. Factura/Ticket</h4>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li>Rellena todos los campos</li>
                    <li>Genera o carga QR (opcional)</li>
                    <li>Elige formato de guardado</li>
                </ol>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 15px; border-radius: 6px; border: 1px solid #4a6572;">
                <h4 style=" margin-top: 0; font-weight: 400;">3. Guardado</h4>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li><strong>Carpeta:</strong> HTML + QR PNG</li>
                    <li><strong>Solo HTML:</strong> QR embebido</li>
                    <li>Selecciona ubicación</li>
                </ol>
            </div>
        </div>
    </div>

     <br>
   <hr>
    
    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #4a6572; font-size: 0.9em;">
        <p style="margin: 5px 0;">
            <strong>ArcaLinux Desktop</strong>
        </p>
        <p style="margin: 5px 0;">
            © 2026 Luigi Adducci | Arcynox - Todos los derechos del software reservados
        </p>
        <p style="margin: 5px 0; font-style: italic;">
            Email: luigiadduccidev@gmail.com - Github: LuigiValentino
        </p>
    </div>
    <br>
    </div>
        """
        
        label = QLabel(about_text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(label)
        
        layout.addWidget(scroll)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArcaLinux - Desktop App")
        
        icon_path = resource_path("resources/app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            QApplication.setWindowIcon(QIcon(icon_path))
        else:
            self.create_fallback_icon()
        
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(QRGeneratorTab(), "QR de Arca")
        self.tab_widget.addTab(FacturaTab(), "Factura")
        self.tab_widget.addTab(TicketTab(), "Ticket")
        self.tab_widget.addTab(AboutTab(), "Acerca de")
        
        self.setCentralWidget(self.tab_widget)
        
        self.statusBar().showMessage("Listo")
        
        self.adjustSize()
        
        self.setMinimumSize(self.size())
    
    def create_fallback_icon(self):
        """Crea un icono simple si no se encuentra el archivo de icono"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#3498db"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", 32, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "A")
        painter.end()
        
        self.setWindowIcon(QIcon(pixmap))
        QApplication.setWindowIcon(QIcon(pixmap))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ArcaLinux")
    app.setOrganizationName("Arcynox")
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
