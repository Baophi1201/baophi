import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_settings():
    """Load cài đặt từ file settings.json."""
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        print("File settings.json không tồn tại.")
        return {}
    except json.JSONDecodeError:
        print("Lỗi định dạng trong settings.json.")
        return {}

def start_work_process(account_data):
    """ Hàm xử lý công việc sau khi đăng nhập """
    print(f"Bắt đầu xử lý công việc cho tài khoản: {account_data['tkfb']}")

    # Thực hiện các công việc cần thiết sau khi đăng nhập thành công vào Facebook và GoLike
    # Ví dụ: gọi các bước tiếp theo trong quy trình làm việc như nhấn nút, tìm job...
    try:
        # Bạn có thể thêm logic xử lý công việc ở đây
        # Ví dụ, mở GoLike và thực hiện các công việc tự động
        print(f"Đang xử lý công việc cho tài khoản {account_data['tkfb']}...")
    except Exception as e:
        print(f"Lỗi khi xử lý công việc: {e}")


def create_chromedriver(tkfb, settings):
    """Tạo một phiên ChromeDriver với profile riêng cho tài khoản."""
    try:
        profile_path = settings.get("profile_folder")
        if not profile_path or not os.path.isdir(profile_path):
            raise ValueError("Đường dẫn profile không hợp lệ trong settings.json.")

        account_profile_path = os.path.join(profile_path, tkfb)
        if not os.path.exists(account_profile_path):
            os.makedirs(account_profile_path)

        chromedriver_path = settings.get("chromedriver")
        if not chromedriver_path or not os.path.isfile(chromedriver_path):
            raise ValueError("Đường dẫn ChromeDriver không hợp lệ trong settings.json.")

        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={account_profile_path}")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")

        driver_service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        print(f"ChromeDriver đã mở với profile: {account_profile_path}")
        return driver
    except Exception as e:
        print(f"Lỗi khi tạo ChromeDriver: {e}")
        raise

def check_and_click_dahieu(driver):
    """Kiểm tra và nhấn nút 'Đã hiểu' nếu xuất hiện."""
    try:
        dahieu_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Đã hiểu')]"))
        )
        if dahieu_button.is_displayed():
            dahieu_button.click()
            print("Đã nhấn nút 'Đã hiểu'.")
    except Exception:
        pass  # Không có nút "Đã hiểu" cũng không phải là lỗi.

def check_job_type(driver):
    """Kiểm tra loại job hiện tại trên GoLike."""
    try:
        job_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h5[contains(@class, 'job-title')]"))
        )
        job_name = job_name_element.text.strip()
        print(f"Tên job: {job_name}")
        return "like" if "TĂNG LIKE CHO BÀI VIẾT" in job_name.upper() else "other"
    except Exception as e:
        print(f"Lỗi khi kiểm tra loại job: {e}")
        return "unknown"

def open_facebook_job(driver):
    """Mở liên kết Facebook của job hiện tại."""
    try:
        fb_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'facebook.com')]"))
        )
        fb_link.click()
        print("Đã mở liên kết Facebook.")
        driver.switch_to.window(driver.window_handles[-1])
        print("Đã chuyển sang tab Facebook.")
    except Exception as e:
        print(f"Lỗi khi mở liên kết Facebook: {e}")

def perform_like_action(driver, thao_tac_time):
    """Thực hiện thao tác Like trên Facebook."""
    try:
        print(f"Đợi {thao_tac_time} giây trước khi nhấn nút Like...")
        WebDriverWait(driver, thao_tac_time).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Thích' or @aria-label='Like']"))
        ).click()
        print("Đã nhấn nút Like.")
    except Exception as e:
        print(f"Không tìm thấy nút Like hoặc bài viết: {e}")
        report_error(driver)

def report_error(driver):
    """Báo lỗi khi không tìm thấy nút Like hoặc bài viết."""
    try:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        error_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Báo lỗi')]")
        error_button.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        send_error_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Gửi báo lỗi')]"))
        )
        send_error_button.click()
        print("Đã gửi báo lỗi.")
        ok_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'OK')]"))
        )
        ok_button.click()
        print("Đã nhấn nút OK sau khi báo lỗi.")
    except Exception as e:
        print(f"Lỗi khi báo lỗi: {e}")

def complete_job(driver):
    """Hoàn thành job trên GoLike."""
    try:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        complete_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Hoàn thành')]")
        complete_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'OK')]"))
        ).click()
        print("Job đã hoàn thành.")
    except Exception as e:
        print(f"Lỗi khi hoàn thành job: {e}")

def main_workflow(driver):
    """Quy trình làm việc chính."""
    try:
        check_and_click_dahieu(driver)
        job_type = check_job_type(driver)
        if job_type == "like":
            open_facebook_job(driver)
            settings = load_settings()
            thao_tac_time = settings.get("thoi_gian_thao_tac", 15)
            perform_like_action(driver, thao_tac_time)
            complete_job(driver)
        else:
            print("Loại job không được hỗ trợ.")
    except Exception as e:
        print(f"Lỗi trong quy trình làm việc chính: {e}")

if __name__ == "__main__":
    settings = load_settings()
    if settings:
        driver = create_chromedriver("sample_account", settings)
        try:
            main_workflow(driver)
        finally:
            driver.quit()
