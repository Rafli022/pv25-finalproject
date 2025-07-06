import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem
)
from PyQt5.uic import loadUi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class KontenNegatifApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("report.ui", self)
        self.setWindowTitle("Aplikasi Pelaporan Konten Negatif")
        self.statusBar().showMessage("Rafli - F1D022022")

        self.koneksiDatabase()
        self.loadData()

        # Tombol
        self.btnTambah.clicked.connect(self.tambahData)
        self.btnHapus.clicked.connect(self.hapusData)
        self.btnEkspor.clicked.connect(self.eksporPDF)
        self.btnKeluar.clicked.connect(self.keluarAplikasi)

        # Menu
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.tentang)

        # StyleSheet Customization
        self.applyCustomStyles()

    def applyCustomStyles(self):
        self.btnTambah.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 6px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btnHapus.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btnEkspor.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #bdc3c7;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 4px;
            }
        """)
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #ecf0f1;
                font-weight: bold;
            }
        """)
        self.btnKeluar.setStyleSheet("""
    QPushButton {
        background-color: #95a5a6;
        color: white;
        padding: 6px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #7f8c8d;
    }
""")

            
    def koneksiDatabase(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                kategori TEXT,
                tanggal TEXT,
                status TEXT,
                keterangan TEXT,
                link TEXT
            )
        """)
        self.conn.commit()

    def loadData(self):
        self.tableWidget.setRowCount(0)
        self.cursor.execute("SELECT judul, kategori, tanggal, keterangan, link, status FROM reports")
        for row_num, row_data in enumerate(self.cursor.fetchall()):
            self.tableWidget.insertRow(row_num)
            for col_num, data in enumerate(row_data[1:]):  # Skip 'id'
                self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def tambahData(self):
        judul = self.inputJudul.text().strip()
        kategori = self.comboKategori.currentText()
        tanggal = self.inputTanggal.date().toString("yyyy-MM-dd")
        status = self.comboStatus.currentText()
        keterangan = self.inputKeterangan.toPlainText().strip()
        link = self.inputLink.text().strip()

        if not judul:
            QMessageBox.warning(self, "Input Salah", "Judul tidak boleh kosong.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO reports (judul, kategori, tanggal, status, keterangan, link)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (judul, kategori, tanggal, status, keterangan, link))
            self.conn.commit()
            self.loadData()

            # Kosongkan form
            self.inputJudul.clear()
            self.inputLink.clear()
            self.inputKeterangan.clear()
            self.comboKategori.setCurrentIndex(0)
            self.comboStatus.setCurrentIndex(0)

            QMessageBox.information(self, "Sukses", "Data berhasil ditambahkan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{e}")

    def hapusData(self):
        baris = self.tableWidget.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Pilih Baris", "Pilih data yang ingin dihapus.")
            return

        judul = self.tableWidget.item(baris, 0).text()
        try:
            self.cursor.execute("DELETE FROM reports WHERE judul=?", (judul,))
            self.conn.commit()
            self.loadData()
            QMessageBox.information(self, "Berhasil", "Data berhasil dihapus.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menghapus data:\n{e}")

    def eksporPDF(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "", "PDF Files (*.pdf)")
        if filename:
            try:
                c = canvas.Canvas(filename, pagesize=A4)
                width, height = A4
                y = height - 50

                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "Laporan Konten Negatif")
                y -= 30
                c.setFont("Helvetica", 10)

                self.cursor.execute("SELECT * FROM reports")
                rows = self.cursor.fetchall()
                for row in rows:
                    text = f"Judul: {row[1]} | Kategori: {row[2]} | Tanggal: {row[3]} | Status: {row[4]}"
                    c.drawString(50, y, text)
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = height - 50

                c.save()
                QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal ekspor PDF:\n{e}")

    def tentang(self):
        QMessageBox.information(self, "Tentang", "Aplikasi ini dibuat oleh Rafli - F1D022022 untuk pelaporan konten negatif.")

    def keluarAplikasi(self):
        self.close()
       
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KontenNegatifApp()
    window.show()
    sys.exit(app.exec_())
