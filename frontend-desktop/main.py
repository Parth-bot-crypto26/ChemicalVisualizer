import sys
import requests
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QTableWidget, 
                             QTableWidgetItem, QHBoxLayout, QFrame, QMessageBox, QLineEdit, QDialog, QListWidget)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_URL = "http://127.0.0.1:8000/api"

# --- 1. LOGIN DIALOG (The Gatekeeper) ---
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Required")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit()
        layout.addWidget(self.user_input)

        layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.attempt_login)
        layout.addWidget(self.btn_login)
        
        self.token = None

    def attempt_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        try:
            resp = requests.post(f"{API_URL}/login/", json={'username': username, 'password': password})
            
            if resp.status_code == 200:
                self.token = resp.json()['token']
                self.accept() 
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid Username or Password")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Cannot connect to Backend.\nMake sure Django is running!\n\nError: {e}")

# --- 2. CHART CANVAS ---
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

# --- 3. MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token 
        self.setWindowTitle("Chemical Equipment Visualizer (Pro)")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_panel = QVBoxLayout()
        self.btn_upload = QPushButton("Upload New CSV")
        self.btn_upload.setStyleSheet("padding: 15px; background: #007bff; color: white; font-weight: bold; font-size: 14px;")
        self.btn_upload.clicked.connect(self.upload_file)
        left_panel.addWidget(self.btn_upload)
        
        left_panel.addWidget(QLabel("<b>Recent History (Click to PDF):</b>"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.download_pdf)
        left_panel.addWidget(self.history_list)
        
        layout.addLayout(left_panel, 1)

        right_panel = QVBoxLayout()
        
        self.stats_label = QLabel("Status: Ready to analyze...")
        self.stats_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.stats_label.setStyleSheet("padding: 10px; background: #f8f9fa; font-size: 14px;")
        right_panel.addWidget(self.stats_label)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        right_panel.addWidget(self.canvas)

        self.table = QTableWidget()
        right_panel.addWidget(self.table)
        
        layout.addLayout(right_panel, 3)
        
        self.refresh_history()

    def refresh_history(self):
        try:
            
            headers = {'Authorization': f'Token {self.token}'}
            resp = requests.get(f"{API_URL}/analyze/", headers=headers)
            if resp.status_code == 200:
                self.history_data = resp.json()
                self.history_list.clear()
                for rec in self.history_data:
                    self.history_list.addItem(f"{rec['file_name']} (ID: {rec['id']})")
        except: pass

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV files (*.csv)")
        if fname:
            try:
                self.stats_label.setText("Uploading... Please wait.")
                QApplication.processEvents()

                files = {'file': open(fname, 'rb')}
                headers = {'Authorization': f'Token {self.token}'}
                
                resp = requests.post(f"{API_URL}/analyze/", files=files, headers=headers)
                
                if resp.status_code == 201:
                    data = resp.json()
                    self.update_ui(data)
                    self.refresh_history()
                    self.stats_label.setText("Success: Data Visualized Below.")
                elif resp.status_code == 401:
                     QMessageBox.warning(self, "Error", "Session Expired. Please restart app and login.")
                else:
                    self.stats_label.setText(f"Error: Server returned {resp.status_code}")
                    print(resp.text)

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def update_ui(self, data):
        stats = data['stats']
        self.stats_label.setText(f"✅ Analysis Complete | Temp: {stats['avg_temp']:.1f}°C | Pressure: {stats['avg_pressure']:.1f} atm | Count: {stats['total_count']}")

        dist = stats['type_distribution']
        self.canvas.axes.cla()
        self.canvas.axes.bar(dist.keys(), dist.values(), color='#28a745')
        self.canvas.axes.set_title("Equipment Type Distribution")
        self.canvas.draw()

        rows = data['preview_data']
        if rows:
            self.table.setColumnCount(len(rows[0]))
            self.table.setRowCount(len(rows))
            self.table.setHorizontalHeaderLabels(rows[0].keys())
            for i, row in enumerate(rows):
                for j, (key, val) in enumerate(row.items()):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def download_pdf(self, item):
        try:
            text = item.text()
            if "ID: " not in text: return
            record_id = text.split("ID: ")[1].split(")")[0]
            
            save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", f"Report_{record_id}.pdf", "PDF Files (*.pdf)")
            
            if save_path:
                self.stats_label.setText("Downloading PDF...")
                QApplication.processEvents()
                
                headers = {'Authorization': f'Token {self.token}'}
                resp = requests.get(f"{API_URL}/report/{record_id}/", headers=headers)
                
                if resp.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(resp.content)
                    QMessageBox.information(self, "Success", f"PDF Saved successfully to:\n{save_path}")
                    self.stats_label.setText("PDF Downloaded.")
                else:
                    QMessageBox.warning(self, "Error", "Could not download PDF from server.")
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    STYLE_SHEET = """
        QMainWindow {
            background-color: #f0f2f5; 
        }
        QLabel {
            font-family: "Segoe UI", sans-serif;
            font-size: 14px;
            color: #333;
        }
        /* Buttons */
        QPushButton {
            background-color: #2a5298;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-family: "Segoe UI", sans-serif;
            border: none;
        }
        QPushButton:hover {
            background-color: #1e3c72;
        }
        QPushButton:pressed {
            background-color: #162c52;
        }
        
        /* Input Fields */
        QLineEdit {
            border: 2px solid #ddd;
            border-radius: 6px;
            padding: 6px;
            background-color: white;
            selection-background-color: #2a5298;
        }
        QLineEdit:focus {
            border: 2px solid #2a5298;
        }

        /* Lists & Tables */
        QListWidget, QTableWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 5px;
            outline: none;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        QListWidget::item:selected {
            background-color: #e8f0fe;
            color: #1a73e8;
            border-left: 3px solid #1a73e8;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 6px;
            border: none;
            border-bottom: 2px solid #ddd;
            font-weight: bold;
            color: #555;
        }
    """
    app.setStyleSheet(STYLE_SHEET)

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        w = MainWindow(login.token)
        w.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)