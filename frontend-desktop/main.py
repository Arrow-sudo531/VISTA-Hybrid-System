import sys
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QFrame, QLineEdit, QDialog, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("V.I.S.T.A. System Gateway")
        self.setFixedSize(900, 550)
        self.api_url = 'http://127.0.0.1:8000/api/login/'
        self.user_data = None
        
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- LEFT PANEL ---
        self.brand_panel = QFrame()
        self.brand_panel.setObjectName("brandPanel")
        self.brand_panel.setFixedWidth(420)
        self.brand_panel.setStyleSheet("#brandPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #2563eb); }")
        
        brand_layout = QVBoxLayout(self.brand_panel)
        brand_layout.setContentsMargins(50, 50, 50, 50)
        
        logo = QLabel("V.I.S.T.A.")
        logo.setStyleSheet("color: white; font-size: 48px; font-weight: 900; letter-spacing: 2px;")
        tagline = QLabel("CHEMICAL TELEMETRY")
        tagline.setStyleSheet("color: #93c5fd; font-size: 12px; font-weight: bold; letter-spacing: 3px;")
        
        brand_layout.addStretch(1)
        brand_layout.addWidget(logo)
        brand_layout.addWidget(tagline)
        brand_layout.addStretch(1)
        
        # --- RIGHT PANEL ---
        self.login_panel = QWidget()
        self.login_panel.setStyleSheet("background-color: #ffffff;")
        login_layout = QVBoxLayout(self.login_panel)
        login_layout.setContentsMargins(70, 60, 70, 60)

        title = QLabel("Sign In")
        title.setStyleSheet("color: #0f172a; font-size: 32px; font-weight: 800;")

        input_style = "padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; background-color: #f8fafc; color: #1e293b;"

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(input_style)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setStyleSheet(input_style)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12px;")

        login_btn = QPushButton("Access Dashboard")
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("background-color: #2563eb; color: white; border-radius: 6px; padding: 15px; font-weight: bold;")

        login_layout.addWidget(title)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.status_lbl)
        login_layout.addWidget(login_btn)
        
        self.main_layout.addWidget(self.brand_panel)
        self.main_layout.addWidget(self.login_panel)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_lbl.setText("Fields cannot be empty")
            return

        try:
            response = requests.post(
                self.api_url, 
                json={"username": username, "password": password}, 
                timeout=5
            )
            
            if response.status_code == 200:
                self.user_data = response.json()
                self.accept()
            else:
                self.status_lbl.setText("Invalid username or password")
        except requests.exceptions.ConnectionError:
            self.status_lbl.setText("Backend server is offline")
        except Exception as e:
            self.status_lbl.setText(f"Error: {str(e)}")


class DesktopDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("V.I.S.T.A. Desktop Pro")
        self.resize(1400, 800)
        self.api_url = 'http://127.0.0.1:8000/api/upload/'
        self.history_url = 'http://127.0.0.1:8000/api/history/'
        self.init_ui()
        self.load_history()

    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: #0f172a;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        logo = QLabel("V.I.S.T.A.")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: 900; margin: 20px;")
        sidebar_layout.addWidget(logo)

        self.upload_btn = QPushButton("Import Dataset")
        self.upload_btn.clicked.connect(self.upload_dataset)
        self.upload_btn.setStyleSheet("background-color: #2563eb; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        sidebar_layout.addWidget(self.upload_btn)
        
        # History Section in Sidebar
        history_title = QLabel("RECENT UPLOADS")
        history_title.setStyleSheet("color: #64748b; font-size: 10px; font-weight: bold; letter-spacing: 2px; margin-top: 30px; margin-left: 10px;")
        sidebar_layout.addWidget(history_title)
        
        # Scrollable history area
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setContentsMargins(10, 10, 10, 10)
        self.history_layout.setSpacing(8)
        
        self.history_scroll.setWidget(self.history_widget)
        sidebar_layout.addWidget(self.history_scroll)
        
        sidebar_layout.addStretch()

        self.status_lbl = QLabel("● System Online")
        self.status_lbl.setStyleSheet("color: #10b981; font-weight: bold; margin-bottom: 20px;")
        sidebar_layout.addWidget(self.status_lbl)

        # Workspace
        self.workspace = QWidget()
        self.workspace.setStyleSheet("background-color: #f1f5f9;")
        workspace_layout = QVBoxLayout(self.workspace)
        workspace_layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel(f"Operational Dashboard | Welcome {self.user_data['username']}")
        header.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
        workspace_layout.addWidget(header)

        self.metrics_layout = QHBoxLayout()
        self.total_card = self.create_card("Total Samples", "--")
        self.pressure_card = self.create_card("Avg Pressure", "--")
        self.temp_card = self.create_card("Mean Temp", "--")
        
        self.metrics_layout.addWidget(self.total_card)
        self.metrics_layout.addWidget(self.pressure_card)
        self.metrics_layout.addWidget(self.temp_card)
        workspace_layout.addLayout(self.metrics_layout)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        workspace_layout.addWidget(self.canvas)

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.workspace)

    def create_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;")
        l = QVBoxLayout(card)
        t = QLabel(title.upper())
        t.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v = QLabel(value)
        v.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
        v.setObjectName("value_label")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def load_history(self):
        """Fetch and display upload history"""
        try:
            headers = {"Authorization": f"Token {self.user_data['token']}"}
            response = requests.get(self.history_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                history_data = response.json()
                self.display_history(history_data)
            else:
                print(f"Failed to load history: {response.status_code}")
        except Exception as e:
            print(f"Error loading history: {str(e)}")

    def display_history(self, history_data):
        """Display history items in the sidebar"""
        # Clear existing history items
        for i in reversed(range(self.history_layout.count())): 
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        if not history_data:
            no_data_label = QLabel("No uploads yet")
            no_data_label.setStyleSheet("color: #475569; font-size: 11px; font-style: italic; padding: 10px;")
            no_data_label.setAlignment(Qt.AlignCenter)
            self.history_layout.addWidget(no_data_label)
            return
        
        # Display each history item
        for item in history_data[:5]:  # Show only last 5
            history_item = self.create_history_item(item)
            self.history_layout.addWidget(history_item)
        
        self.history_layout.addStretch()

    def create_history_item(self, item):
        """Create a widget for a single history item"""
        from datetime import datetime
        
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border: 1px solid #3b82f6;
                background-color: #1e293b;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # File name
        name_label = QLabel(item.get('name', 'Unknown'))
        name_label.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: bold;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Date
        date_str = item.get('date', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%b %d, %Y %H:%M')
            except:
                formatted_date = date_str
        else:
            formatted_date = 'No date'
        
        date_label = QLabel(formatted_date)
        date_label.setStyleSheet("color: #64748b; font-size: 9px; font-family: monospace;")
        layout.addWidget(date_label)
        
        return frame

    def upload_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'rb') as f:
                headers = {"Authorization": f"Token {self.user_data['token']}"}
                try:
                    response = requests.post(self.api_url, files={'file': f}, headers=headers, timeout=10)
                    if response.status_code == 201:
                        self.update_ui(response.json())
                        self.load_history()  # Reload history after upload
                        QMessageBox.information(self, "Success", "Dataset uploaded successfully")
                    else:
                        error_msg = response.json().get('error', f'Server returned {response.status_code}')
                        QMessageBox.warning(self, "Error", error_msg)
                except Exception as e:
                    QMessageBox.critical(self, "Connection Error", str(e))

    def update_ui(self, data):
        try:
            total = data.get('total_count', 'N/A')
            avg_pressure = data.get('averages', {}).get('avg_pressure', 'N/A')
            avg_temp = data.get('averages', {}).get('avg_temp', 'N/A')
            avg_flowrate = data.get('averages', {}).get('avg_flowrate', 'N/A')
            
            self.total_card.findChild(QLabel, "value_label").setText(str(total))
            self.pressure_card.findChild(QLabel, "value_label").setText(f"{avg_pressure} PSI")
            self.temp_card.findChild(QLabel, "value_label").setText(f"{avg_temp} °C")
            
            self.ax.clear()
            self.ax.bar(['Pressure', 'Temp', 'Flow'], 
                        [avg_pressure if isinstance(avg_pressure, (int, float)) else 0, 
                         avg_temp if isinstance(avg_temp, (int, float)) else 0, 
                         avg_flowrate if isinstance(avg_flowrate, (int, float)) else 0], 
                        color=['#2563eb', '#10b981', '#f59e0b'])
            self.ax.set_title("Current Asset Telemetry")
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Data Error", f"Failed to update UI: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        dash = DesktopDashboard(login.user_data)
        dash.show()
        sys.exit(app.exec_())