import sys
import json
import time
from login import start_login_process
from caidatchung import SettingsApp
from themtaikhoan import AddAccountApp
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QMenu, QAction, QFileDialog, QWidget, QHBoxLayout, QLineEdit, QStyledItemDelegate,
    QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from lamviec import start_work_process

class ChromeThread(QThread):
    finished = pyqtSignal(int)  # Signal để thông báo khi đóng xong Chrome
    
    def __init__(self, driver, row):
        super().__init__()
        self.driver = driver
        self.row = row
    
    def run(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        self.finished.emit(self.row)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Golike Tool")
        
        # Thiết lập kích thước cửa sổ
        self.resize(1200, 600)  # Tăng kích thước cửa sổ
        
        # Di chuyển cửa sổ ra giữa màn hình
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # Đọc giá trị chromedriver_path từ settings.json
        self.chromedriver_path = self.get_chromedriver_path()

        # Đảm bảo rằng chromedriver_path đã được xác định
        if self.chromedriver_path:
            print(f"Đường dẫn chromedriver: {self.chromedriver_path}")
        else:
            print("Chưa xác định đường dẫn chromedriver.")

        # Widget và layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Nút "Cài đặt chung" và "Thêm tài khoản" nằm gần nhau và kích thước nhỏ
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)  # Giảm khoảng cách giữa các widget xuống 5px
        
        self.settings_button = QPushButton("Cài đặt chung")
        self.settings_button.setFixedSize(100, 25)  # Kích thước nhỏ hơn
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        
        self.add_account_button = QPushButton("Thêm tài khoản")
        self.add_account_button.setFixedSize(100, 25)  # Kích thước nhỏ hơn
        self.add_account_button.clicked.connect(self.open_add_account)
        button_layout.addWidget(self.add_account_button)

        # Thêm dòng chữ "Thu nhập" vào cùng hàng với các nút
        self.label_income = QLabel("Thu nhập")
        button_layout.addWidget(self.label_income)

        button_layout.addStretch()  # Đẩy các widget về bên trái
        layout.addLayout(button_layout)

        # Thiết lập bảng
        self.table = QTableWidget()
        self.setup_table()

        layout.addWidget(self.table)

        # Thêm xử lý click ra ngoài bảng
        central_widget.setMouseTracking(True)
        central_widget.mousePressEvent = self.on_widget_click

        # Load dữ liệu tài khoản
        self.load_accounts()

    def get_chromedriver_path(self):
        """Đọc đường dẫn chromedriver từ settings.json"""
        try:
            with open("settings.json", "r", encoding='utf-8') as file:
                settings = json.load(file)
                return settings.get("chromedriver_path", "")
        except FileNotFoundError:
            print("Không tìm thấy file settings.json")
            return ""
        except json.JSONDecodeError:
            print("Lỗi đọc file settings.json")
            return ""
        except Exception as e:
            print(f"Lỗi: {str(e)}")
            return ""

    def setup_table(self):
        # Thiết lập bảng
        self.table.setColumnCount(10)  # Tăng số lượng cột từ 9 lên 10
        headers = ["STT", "TK Facebook", "MK Facebook", "TK Golike", "MK Golike", "Cookie", "Proxy", "Job", "Tạm dừng", "Trạng thái"]
        self.table.setHorizontalHeaderLabels(headers)

        # Thiết lập độ rộng cột
        header = self.table.horizontalHeader()
        
        # Cột STT
        self.table.setColumnWidth(0, 50)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        
        # Các cột tài khoản
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Cột Cookie
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        # Cột Job
        self.table.setColumnWidth(7, 60)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        
        # Cột Tạm dừng
        self.table.setColumnWidth(8, 80)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        
        # Cột Trạng thái
        self.table.setColumnWidth(9, 300)  # Tăng độ rộng cột trạng thái
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        
        # Căn giữa header
        for i in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignCenter)

        # Ẩn row header
        self.table.verticalHeader().setVisible(False)

        # Thiết lập chọn dòng và không cho chỉnh sửa
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)  # Cho phép chọn nhiều dòng
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Thiết lập stylesheet cho bảng
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d6d9dc;
                background-color: white;
                alternate-background-color: #f5f5f5;
                outline: none;  /* Bỏ viền focus */
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #b3e5fc;  /* Màu xanh đậm hơn */
                color: black;
                border: none;
            }
            QTableWidget::item:focus {
                border: none;  /* Bỏ viền focus cho item */
                outline: none;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d6d9dc;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #f0f0f0;
                border: 1px solid #d6d9dc;
            }
        """)

        # Thiết lập menu chuột phải
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Kết nối sự kiện keyPressEvent và clicked
        self.table.keyPressEvent = self.handle_key_press
        self.table.clicked.connect(self.on_table_clicked)

    def handle_key_press(self, event):
        # Xử lý Ctrl+A
        if event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            # Bỏ tick tất cả các checkbox
            for row in range(self.table.rowCount()):
                checkbox_widget = self.table.cellWidget(row, 8)
                if checkbox_widget:
                    checkbox = checkbox_widget.layout().itemAt(0).widget()
                    # Ngắt kết nối tạm thởi để tránh trigger sự kiện
                    checkbox.stateChanged.disconnect()
                    checkbox.setChecked(False)
                    checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_changed(state, r))
            # Chọn tất cả các dòng
            self.table.selectAll()
        else:
            # Chuyển các phím khác cho xử lý mặc định
            QTableWidget.keyPressEvent(self.table, event)

    def on_table_clicked(self, index):
        # Nếu click vào cột checkbox, không làm gì cả
        if index.column() == 8:
            return
            
        # Nếu click vào các cột khác, bỏ chọn tất cả checkbox
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 8)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                # Ngắt kết nối tạm thởi để tránh trigger sự kiện
                checkbox.stateChanged.disconnect()
                checkbox.setChecked(False)
                checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_changed(state, r))

    def load_accounts(self):
        """Load account data from a JSON file and populate the table."""
        try:
            # Xóa tất cả các dòng hiện tại trong bảng
            self.table.setRowCount(0)

            # Đọc dữ liệu từ file
            with open("taikhoan.json", "r", encoding='utf-8') as file:
                accounts = json.load(file)

            # Add accounts to the table
            for index, account in enumerate(accounts, 1):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                
                # Create and set items with center alignment
                # Thêm STT
                stt_item = QTableWidgetItem(str(index))
                stt_item.setTextAlignment(Qt.AlignCenter)
                stt_item.setFlags(stt_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_position, 0, stt_item)

                # Thêm các thông tin tài khoản
                for col, value in enumerate([
                    account.get("tkfb", ""),
                    account.get("mkfb", ""),
                    account.get("tkgolike", ""),
                    account.get("mkgolike", ""),
                    account.get("cookie", ""),
                    account.get("proxy", ""),
                    account.get("job", "")
                ], 1):  # Bắt đầu từ cột 1 vì cột 0 là STT
                    item = QTableWidgetItem(str(value))  # Chuyển đổi value thành string
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_position, col, item)

                # Create and add a checkbox to the "Tạm dừng" column
                checkbox = QCheckBox()
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox.stateChanged.connect(lambda state, row=row_position: self.on_checkbox_changed(state, row))
                self.table.setCellWidget(row_position, 8, checkbox_widget)

                # Add status with center alignment
                status_item = QTableWidgetItem("Chưa bắt đầu")
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_position, 9, status_item)

        except FileNotFoundError:
            print("Không tìm thấy file taikhoan.json")
        except json.JSONDecodeError:
            print("Lỗi đọc file taikhoan.json")
        except Exception as e:
            print(f"Lỗi: {str(e)}")

    def on_checkbox_changed(self, state, row):
        if state == Qt.Checked:
            self.table.selectRow(row)
        else:
            self.table.clearSelection()

    def open_settings(self):
        self.settings_window = SettingsApp(self)
        self.settings_window.show()

    def open_add_account(self):
        from themtaikhoan import AddAccountApp
        self.add_account_window = AddAccountApp(self)  # This method should be defined
        self.add_account_window.show()

    def start_task(self, row):
        # Lấy đường dẫn Chromedriver từ settings.json
        chromedriver_path = self.chromedriver_path

        def run_task():
            try:
                # Khởi tạo driver thông qua quá trình login
                account_data = self.get_account_data_from_row(row)  # Lấy thông tin tài khoản
                driver = start_login_process(
                    chromedriver_path, account_data, account_data["tkfb"]  # Truyền tên profile
                )
                
                if driver:
                    # Lưu driver vào dictionary
                    if not hasattr(self, 'drivers'):
                        self.drivers = {}
                    self.drivers[row] = driver
                    
                    # Cập nhật trạng thái
                    status_item = self.table.item(row, 9)
                    if status_item:
                        self.table.item(row, 9).setText("Đang chạy")
                    
                    # Bắt đầu xử lý công việc
                    start_work_process(account_data)
                else:
                    # Cập nhật trạng thái lỗi nếu không khởi tạo được driver
                    status_item = self.table.item(row, 9)
                    if status_item:
                        self.table.item(row, 9).setText("Lỗi khởi tạo")
            
            except Exception as e:
                # Xử lý các ngoại lệ không mong muốn
                print(f"Lỗi khi khởi chạy tài khoản: {e}")
                status_item = self.table.item(row, 9)
                if status_item:
                    self.table.item(row, 9).setText(f"Lỗi: {str(e)}")

        # Chạy task trong thread riêng để không chặn giao diện
        import threading
        task_thread = threading.Thread(target=run_task)
        task_thread.daemon = True
        task_thread.start()

    def get_account_data_from_row(self, row):
        """Retrieve account data from the table row."""
        tkfb = self.table.item(row, 1).text()
        mkfb = self.table.item(row, 2).text()
        tkgolike = self.table.item(row, 3).text()
        mkgolike = self.table.item(row, 4).text()
        cookie = self.table.item(row, 5).text()
        proxy = self.table.item(row, 6).text()
        job = self.table.item(row, 7).text()

        return {
            "tkfb": tkfb,
            "mkfb": mkfb,
            "tkgolike": tkgolike,
            "mkgolike": mkgolike,
            "cookie": cookie,
            "proxy": proxy,
            "job": job
        }

    def show_context_menu(self, position):
        menu = QMenu(self)
        start_action = menu.addAction("Bắt đầu")
        stop_action = menu.addAction("Kết thúc")
        menu.addSeparator()
        delete_action = menu.addAction("Xóa tài khoản")

        # Lấy dòng được chọn
        row = self.table.rowAt(position.y())
        
        # Vô hiệu hóa nút xóa nếu không click vào dòng nào
        if row < 0:
            delete_action.setEnabled(False)
        else:
            # Kiểm tra trạng thái để enable/disable các action
            status_item = self.table.item(row, 9)  # Cột trạng thái
            if status_item:
                status = status_item.text()
                start_action.setEnabled(status in ["Chưa bắt đầu", "Đã dừng"])
                stop_action.setEnabled(status == "Đang chạy")

        # Hiển thị menu và xử lý action được chọn
        action = menu.exec_(self
