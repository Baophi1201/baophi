import json
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QSpinBox, QLineEdit, QPushButton, 
    QFileDialog, QWidget, QHBoxLayout, QGroupBox, QApplication
)


class SettingsApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt chung")
        self.resize(500, 400)
        
        # Di chuyển cửa sổ ra giữa màn hình
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        main_layout = QVBoxLayout()

        # Group box cho thông số
        params_group = QGroupBox("Thông số")
        params_layout = QVBoxLayout()

        # Tạo style chung cho các ô nhập số
        spinbox_width = 45  # Giảm độ rộng xuống
        label_width = 100   # Giảm độ rộng label

        # Số luồng
        threads_layout = QHBoxLayout()
        threads_label = QLabel("Số luồng:")
        threads_label.setFixedWidth(label_width)
        self.num_threads = QSpinBox()
        self.num_threads.setFixedWidth(spinbox_width)
        self.num_threads.setRange(1, 100)
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.num_threads)
        threads_layout.addStretch()
        params_layout.addLayout(threads_layout)

        # Thời gian giữa 2 nick
        time_between_layout = QHBoxLayout()
        time_between_label = QLabel("Thời gian giữa 2 nick:")
        time_between_label.setFixedWidth(label_width)
        self.time_between = QSpinBox()
        self.time_between.setFixedWidth(spinbox_width)
        self.time_between.setRange(1, 300)
        time_between_layout.addWidget(time_between_label)
        time_between_layout.addWidget(self.time_between)
        time_between_layout.addWidget(QLabel("giây"))
        time_between_layout.addStretch()
        params_layout.addLayout(time_between_layout)

        # Thời gian thao tác
        operation_time_layout = QHBoxLayout()
        operation_time_label = QLabel("Thời gian thao tác:")
        operation_time_label.setFixedWidth(label_width)
        self.operation_time = QSpinBox()
        self.operation_time.setFixedWidth(spinbox_width)
        self.operation_time.setRange(1, 600)
        operation_time_layout.addWidget(operation_time_label)
        operation_time_layout.addWidget(self.operation_time)
        operation_time_layout.addWidget(QLabel("giây"))
        operation_time_layout.addStretch()
        params_layout.addLayout(operation_time_layout)

        # Chuyển nick và kết thúc job
        transfer_layout = QHBoxLayout()
        transfer_label = QLabel("Chuyển nick khi đủ:")
        transfer_label.setFixedWidth(label_width)
        self.min_jobs = QSpinBox()
        self.min_jobs.setFixedWidth(spinbox_width)
        self.min_jobs.setRange(1, 100)
        self.max_jobs = QSpinBox()
        self.max_jobs.setFixedWidth(spinbox_width)
        self.max_jobs.setRange(1, 100)
        transfer_layout.addWidget(transfer_label)
        transfer_layout.addWidget(self.min_jobs)
        transfer_layout.addWidget(QLabel("đến"))
        transfer_layout.addWidget(self.max_jobs)
        transfer_layout.addWidget(QLabel("job"))
        transfer_layout.addStretch()
        params_layout.addLayout(transfer_layout)

        # Kết thúc job
        finish_jobs_layout = QHBoxLayout()
        finish_jobs_label = QLabel("Kết thúc khi đủ:")
        finish_jobs_label.setFixedWidth(label_width)
        self.finish_jobs = QSpinBox()
        self.finish_jobs.setFixedWidth(spinbox_width)
        self.finish_jobs.setRange(1, 1000)
        finish_jobs_layout.addWidget(finish_jobs_label)
        finish_jobs_layout.addWidget(self.finish_jobs)
        finish_jobs_layout.addWidget(QLabel("job"))
        finish_jobs_layout.addStretch()
        params_layout.addLayout(finish_jobs_layout)

        # Thêm spacing cho params_layout
        params_layout.setSpacing(10)  # Khoảng cách giữa các dòng
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # Group box cho đường dẫn
        paths_group = QGroupBox("Đường dẫn")
        paths_layout = QVBoxLayout()
        paths_layout.setSpacing(10)  # Khoảng cách giữa các dòng

        # Độ rộng cố định cho nút và label
        button_width = 60
        path_label_width = 100
        
        # Tạo style cho QLineEdit
        line_edit_style = """
            QLineEdit {
                margin-right: 5px;
            }
        """

        # Profile path
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(5)  # Giảm khoảng cách giữa các widget
        profile_label = QLabel("Profile:")
        profile_label.setFixedWidth(path_label_width)
        self.profile_path = QLineEdit()
        self.profile_path.setStyleSheet(line_edit_style)
        self.btn_profile = QPushButton("Chọn")
        self.btn_profile.setFixedWidth(button_width)
        self.btn_profile.clicked.connect(self.select_folder_profile)
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_path)
        profile_layout.addWidget(self.btn_profile)
        paths_layout.addLayout(profile_layout)

        # Chromedriver path
        chrome_layout = QHBoxLayout()
        chrome_layout.setSpacing(5)  # Giảm khoảng cách giữa các widget
        chrome_label = QLabel("Chromedriver:")
        chrome_label.setFixedWidth(path_label_width)
        self.chromedriver_path = QLineEdit()
        self.chromedriver_path.setStyleSheet(line_edit_style)
        self.btn_chromedriver = QPushButton("Chọn")
        self.btn_chromedriver.setFixedWidth(button_width)
        self.btn_chromedriver.clicked.connect(self.select_file_chromedriver)
        chrome_layout.addWidget(chrome_label)
        chrome_layout.addWidget(self.chromedriver_path)
        chrome_layout.addWidget(self.btn_chromedriver)
        paths_layout.addLayout(chrome_layout)

        # Captcha extension path
        captcha_layout = QHBoxLayout()
        captcha_layout.setSpacing(5)  # Giảm khoảng cách giữa các widget
        captcha_label = QLabel("Extension:")
        captcha_label.setFixedWidth(path_label_width)
        self.captcha_extension = QLineEdit()
        self.captcha_extension.setStyleSheet(line_edit_style)
        self.btn_captcha = QPushButton("Chọn")
        self.btn_captcha.setFixedWidth(button_width)
        self.btn_captcha.clicked.connect(self.select_file_captcha)
        captcha_layout.addWidget(captcha_label)
        captcha_layout.addWidget(self.captcha_extension)
        captcha_layout.addWidget(self.btn_captcha)
        paths_layout.addLayout(captcha_layout)

        paths_group.setLayout(paths_layout)
        main_layout.addWidget(paths_group)

        # Nút lưu
        self.btn_save = QPushButton("Lưu cài đặt")
        main_layout.addWidget(self.btn_save)
        self.btn_save.clicked.connect(self.save_settings)

        # Thêm spacing cho main_layout
        main_layout.setSpacing(15)  # Khoảng cách giữa các group box

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load settings nếu đã tồn tại
        self.load_settings()

    def select_folder_profile(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục Profile")
        if folder:
            self.profile_path.setText(folder)

    def select_file_chromedriver(self):
        file, _ = QFileDialog.getOpenFileName(self, "Chọn tệp Chromedriver", "", "Executable Files (*.exe)")
        if file:
            self.chromedriver_path.setText(file)

    def select_file_captcha(self):
        file, _ = QFileDialog.getOpenFileName(self, "Chọn tệp Extension", "", "CRX Files (*.crx)")
        if file:
            self.captcha_extension.setText(file)

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding='utf-8') as f:
                settings = json.load(f)
                self.num_threads.setValue(settings.get("Số luồng", 1))
                self.time_between.setValue(settings.get("Thời gian giữa 2 nick", 1))
                self.operation_time.setValue(settings.get("Thời gian thao tác", 1))
                self.min_jobs.setValue(settings.get("Số job tối thiểu", 1))
                self.max_jobs.setValue(settings.get("Số job tối đa", 1))
                self.finish_jobs.setValue(settings.get("Số job kết thúc", 1))
                self.profile_path.setText(settings.get("profile_path", ""))
                self.chromedriver_path.setText(settings.get("chromedriver_path", ""))
                self.captcha_extension.setText(settings.get("captcha_extension", ""))
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            "Số luồng": self.num_threads.value(),
            "Thời gian giữa 2 nick": self.time_between.value(),
            "Thời gian thao tác": self.operation_time.value(),
            "Số job tối thiểu": self.min_jobs.value(),
            "Số job tối đa": self.max_jobs.value(),
            "Số job kết thúc": self.finish_jobs.value(),
            "profile_path": self.profile_path.text().strip(),
            "chromedriver_path": self.chromedriver_path.text().strip(),
            "captcha_extension": self.captcha_extension.text().strip()
        }

        with open("settings.json", "w", encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

        self.close()