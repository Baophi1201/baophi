import json
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QTextEdit, QPushButton, QLabel, QWidget, QApplication
)
from PyQt5.QtCore import Qt

class AddAccountApp(QMainWindow):
    def __init__(self, main_window): 
        super().__init__()
        self.setWindowTitle("Thêm tài khoản")
        self.resize(600, 400)  # Set the window size
        
        # Move the window to the center of the screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        self.main_window = main_window

        layout = QVBoxLayout()

        # Ô nhập tài khoản (được chỉnh kích thước to hơn)
        self.account_input = QTextEdit()  # Đổi từ QLineEdit sang QTextEdit
        self.account_input.setPlaceholderText("Nhập tài khoản theo định dạng: tkfb|mkfb|tkgolike|mkgolike|proxy\nMỗi tài khoản một dòng")
        self.account_input.setFixedHeight(300)  # Set a fixed height for the input field
        self.account_input.setFixedWidth(600)  # Set a fixed width for the input field (wider)
        
        # Align the placeholder text to the left
        self.account_input.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Adding some padding to ensure the text stays at the top-left
        self.account_input.setStyleSheet("padding-top: 10px; padding-left: 10px;")
        
        layout.addWidget(self.account_input)

        # Nút thêm tài khoản
        self.btn_add = QPushButton("Thêm")
        self.btn_add.clicked.connect(self.add_accounts)  # Đổi tên hàm thành add_accounts
        layout.addWidget(self.btn_add)

        # Thiết lập widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_accounts(self):
        # Lấy toàn bộ nội dung và tách thành từng dòng
        content = self.account_input.toPlainText().strip()
        if not content:
            return

        # Tách thành từng dòng và lọc bỏ dòng trống
        account_lines = [line.strip() for line in content.split('\n') if line.strip()]

        try:
            # Đọc danh sách tài khoản hiện có
            try:
                with open("taikhoan.json", "r", encoding='utf-8') as f:
                    accounts = json.load(f)
            except FileNotFoundError:
                accounts = []

            # Xử lý từng dòng tài khoản
            for line in account_lines:
                account_data = line.split("|")
                if len(account_data) == 5:
                    new_account = {
                        "tkfb": account_data[0].strip(),
                        "mkfb": account_data[1].strip(),
                        "tkgolike": account_data[2].strip(),
                        "mkgolike": account_data[3].strip(),
                        "proxy": account_data[4].strip(),
                    }

                    # Kiểm tra xem tài khoản đã tồn tại chưa
                    account_exists = False
                    for i, account in enumerate(accounts):
                        if account["tkfb"] == new_account["tkfb"]:
                            # Cập nhật thông tin tài khoản
                            accounts[i] = new_account
                            account_exists = True
                            break

                    # Nếu tài khoản chưa tồn tại, thêm mới
                    if not account_exists:
                        accounts.append(new_account)

            # Lưu lại vào file
            with open("taikhoan.json", "w", encoding='utf-8') as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)

            # Cập nhật lại TreeView trong gui.py
            self.main_window.load_accounts()
            
            # Đóng cửa sổ thêm tài khoản
            self.close()
        except Exception as e:
            print(f"Lỗi khi thêm tài khoản: {str(e)}")
