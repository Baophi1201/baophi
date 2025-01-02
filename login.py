import threading
import queue
import traceback
import random
import json
import time
import os
import zipfile
import tempfile
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    SessionNotCreatedException,
    NoSuchElementException,
)

def proxies(proxy_config):
    """Hàm tạo Chrome extension với proxy và authentication từ cấu hình proxy"""
    try:
        # Trích xuất thông tin proxy
        host = proxy_config["host"]
        port = proxy_config["port"]
        username = proxy_config["username"]
        password = proxy_config["password"]

        # Tạo thư mục extension nếu chưa tồn tại
        extension_dir = os.path.join(os.getcwd(), "proxy_extension")
        os.makedirs(extension_dir, exist_ok=True)

        # Tạo manifest.json
        manifest_path = os.path.join(extension_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(
                """{
                "manifest_version": 3,
                "name": "Proxy Authentication",
                "version": "1.0",
                "description": "Proxy Authentication Extension",
                "permissions": [
                    "proxy",
                    "webRequest",
                    "webRequestBlocking",
                    "<all_urls>"
                ],
                "background": {
                    "service": "background.js"
                }
            }"""
            )

        # Tạo background.js
        background_path = os.path.join(extension_dir, "background.js")
        with open(background_path, "w", encoding="utf-8") as f:
            f.write(
                f"""
            // Cấu hình proxy
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{host}",
                        port: {port}
                    }},
                    bypassList: ["localhost", "127.0.0.1"]
                }}
            }};

            // Thiết lập proxy
            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            // Xử lý xác thực proxy
            function callbackFn(details) {{
                return {{
                    authCredentials: {{
                        username: "{username}",
                        password: "{password}"
                    }}
                }};
            }}

            // Đăng ký listener cho xác thực proxy
            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );

            // Ghi log để debug
            console.log('Proxy configuration loaded: ' + JSON.stringify(config));
            """
            )

        print(f"Tạo proxy extension: {host}:{port} với user {username}")
        return extension_dir
    except OSError as e:
        print(f"Lỗi khi tạo thư mục hoặc ghi file: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi tạo proxy extension: {e}")
        traceback.print_exc()
        return None


def prepare_extension(extension_path):
    """Chuẩn bị extension bằng cách giải nén và kiểm tra manifest"""
    extension_dir = tempfile.mkdtemp(prefix="chrome_extension_")
    try:
        # Tên thư mục extension dựa trên tên file
        extension_name = os.path.splitext(os.path.basename(extension_path))[0]
        full_extension_dir = os.path.join(extension_dir, extension_name)

        # Tạo thư mục mới
        os.makedirs(full_extension_dir, exist_ok=True)

        # Giải nén extension
        with zipfile.ZipFile(extension_path, "r") as zip_ref:
            zip_ref.extractall(full_extension_dir)

        # Kiểm tra manifest
        manifest_path = os.path.join(full_extension_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"KHÔNG TÌM THẤY manifest.json trong {extension_path}")

        # Đọc và in nội dung manifest (để debug)
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            print(f"Manifest của extension {extension_name}:")
            print(json.dumps(manifest, indent=2))

        return full_extension_dir
    except (FileNotFoundError, zipfile.BadZipFile, json.JSONDecodeError) as e:
        print(f"Lỗi khi giải nén hoặc đọc manifest: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi chuẩn bị extension: {e}")
        traceback.print_exc()
        return None
    finally:
        shutil.rmtree(extension_dir, ignore_errors=True)


def create_chrome_options(proxy_config=None):
    """Tạo cấu hình Chrome Options"""
    options = webdriver.ChromeOptions()

    # User Agent đa dạng
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Các tùy chọn tối ưu
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")

    # Thêm các tùy chọn để tăng tính ổn định
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # Argument chống phát hiện bot
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Danh sách các extension
    extensions = []

    # Proxy với extension
    if proxy_config and proxy_config.get("host") and proxy_config.get("port"):
        # Cấu hình proxy chi tiết
        proxy_url = f"{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"

        # Thêm proxy server với xác thực
        options.add_argument(f"--proxy-server={proxy_url}")

        # Tạo extension proxy
        try:
            proxy_extension = proxies(proxy_config)
            if proxy_extension:
                prepared_proxy_extension = prepare_extension(proxy_extension)
                if prepared_proxy_extension:
                    extensions.append(prepared_proxy_extension)
        except Exception as e:
            print(f"Lỗi tạo proxy extension: {e}")
            traceback.print_exc()

        # Thêm các tùy chọn proxy bổ sung
        options.add_argument("--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost")
        options.add_argument("--proxy-bypass-list=localhost,127.0.0.1")

        # Thêm các tùy chọn kết nối proxy
        options.add_argument("--enable-proxy-resolver")
        options.add_argument("--proxy-connection-timeout=30")

    # Thêm extension captcha từ settings.json
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            settings = json.load(file)

        captcha_extension_paths = [
            settings.get("captcha_extension_path", ""),
            settings.get("captcha_extension_path_2", ""),
        ]
        for captcha_extension_path in captcha_extension_paths:
            if os.path.exists(captcha_extension_path):
                prepared_captcha_extension = prepare_extension(captcha_extension_path)
                if prepared_captcha_extension:
                    extensions.append(prepared_captcha_extension)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Lỗi đọc settings hoặc thêm extension captcha: {e}")
        traceback.print_exc()

    # Thêm tất cả các extension
    if extensions:
        # Tạo danh sách các extension để load
        extension_paths = ",".join(extensions)

        # Sử dụng lệnh load extension phù hợp với Manifest V3
        options.add_argument(f"--load-extension={extension_paths}")
        options.add_argument("--disable-extensions-except=" + extension_paths)

        print(f"Đã thêm các extension: {extension_paths}")

    return options


def parse_proxy(account_data):
    """Trích xuất proxy từ thông tin tài khoản"""
    try:
        # In ra toàn bộ dữ liệu để debug
        print("Dữ liệu tài khoản:", account_data)

        # Kiểm tra proxy trong các trường khác nhau
        proxy_fields = ["proxy", "proxyfb", "proxygolike"]

        for field in proxy_fields:
            proxy_str = account_data.get(field, "")

            # Nếu proxy có @ thì phân tích
            if proxy_str and "@" in proxy_str:
                # Tách username:password và host:port
                auth, host_port = proxy_str.split("@")
                username, password = auth.split(":")
                host, port = host_port.split(":")

                # Mặc định extension là http
                extension = "http"

                proxy_config = {
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "extension": extension,
                }

                print("Proxy được phân tích:", proxy_config)
                return proxy_config

        print("Không tìm thấy proxy hợp lệ")
        return None
    except (ValueError, KeyError) as e:
        print(f"Lỗi phân tích proxy: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi phân tích proxy: {e}")
        traceback.print_exc()
        return None


class FacebookLogin:
    def __init__(self, chromedriver_path, account_data):
        self.chromedriver_path = chromedriver_path
        self.account_data = account_data
        self.proxy_config = parse_proxy(account_data)
        self.driver = None

    def create_driver(self):
        """Tạo driver với các cấu hình an toàn và tăng tính ổn định"""
        try:
            # In ra thông tin proxy để debug
            print("Proxy config:", self.proxy_config)

            # Thiết lập Service với timeout
            service = Service(
                executable_path=self.chromedriver_path,
                service_args=["--verbose"],
                log_path="chromedriver.log",
            )

            # Tạo options
            options = create_chrome_options(self.proxy_config)

            # Tăng timeout và số lần thử lại
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Khởi tạo driver
                    self.driver = webdriver.Chrome(service=service, options=options)

                    # Cài đặt các timeout
                    self.driver.set_page_load_timeout(30)
                    self.driver.implicitly_wait(10)

                    # Kiểm tra IP hiện tại
                    try:
                        self.driver.get("https://api.ipify.org")
                        current_ip = self.driver.find_element(By.TAG_NAME, "body").text
                        print(f"IP hiện tại: {current_ip}")
                    except Exception as ip_error:
                        print(f"Không thể kiểm tra IP: {ip_error}")

                    return self.driver

                except (WebDriverException, TimeoutException) as e:
                    print(f"Lỗi khởi tạo driver (lần {attempt + 1}): {e}")
                    if self.driver:  # Kiểm tra driver đã được tạo chưa
                        try:
                            self.driver.quit()
                        except:
                            pass
                    time.sleep(2)

            # Nếu vẫn không thành công sau số lần thử quy định
            print("Không thể khởi tạo driver sau nhiều lần thử.")
            return None

        except Exception as e:
            print(f"Lỗi không mong muốn khi tạo driver: {e}")
            traceback.print_exc()
            return None

    def close_driver(self):
        """Đóng driver an toàn"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Lỗi khi đóng driver: {e}")
            finally:
                self.driver = None

    def login_facebook(self):
        """Đăng nhập Facebook"""
        driver = self.create_driver()
        if not driver:
            return None

        try:
            # Log proxy nếu có
            if self.proxy_config:
                print(
                    f"Đang sử dụng proxy: {self.proxy_config['host']}:{self.proxy_config['port']}"
                )

            driver.get("https://www.facebook.com")

            # Chờ và điền thông tin đăng nhập với timeout
            wait = WebDriverWait(driver, 20)

            # Sử dụng WebDriverWait để chờ element xuất hiện
            email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_input = wait.until(
                EC.presence_of_element_located((By.ID, "pass"))
            )

            # Nhập dữ liệu
            email_input.send_keys(self.account_data["tkfb"])
            password_input.send_keys(self.account_data["mkfb"])

            password_input.submit()

            # Chờ đăng nhập thành công
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Menu']")))

            print(f"Đăng nhập Facebook thành công: {self.account_data['tkfb']}")
            return driver

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Lỗi đăng nhập Facebook: {e}")
            traceback.print_exc()
            driver.quit()
            return None
        except Exception as e:
            print(f"Lỗi không xác định khi đăng nhập Facebook: {e}")
            traceback.print_exc()
            driver.quit()
            return None

    def login_golike(self, driver):
        """Đăng nhập GoLike"""
        try:
            driver.get("https://app.golike.net/login")

            wait = WebDriverWait(driver, 20)
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_input = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )

            # Nhập dữ liệu
            username_input.send_keys(self.account_data["tkgolike"])
            password_input.send_keys(self.account_data["mkgolike"])

            password_input.submit()

            # Chờ đăng nhập thành công
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='dashboard']")))

            print(f"Đăng nhập GoLike thành công: {self.account_data['tkgolike']}")
            return driver

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Lỗi đăng nhập GoLike: {e}")
            traceback.print_exc()
            driver.quit()
            return None
        except Exception as e:
            print(f"Lỗi không xác định khi đăng nhập Golike: {e}")
            traceback.print_exc()
            driver.quit()
            return None

    def login(self):
        """Quá trình đăng nhập toàn bộ"""
        try:
            driver = self.login_facebook()
            if driver:
                golike_driver = self.login_golike(driver)
                return golike_driver
