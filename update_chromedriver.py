import os
import requests
import zipfile
import re
import subprocess

def get_chrome_version():
    try:
        # Sử dụng PowerShell để lấy phiên bản Chrome
        result = subprocess.run(['powershell', '-command', 
            '(Get-Item "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe").VersionInfo.ProductVersion'], 
            capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Lỗi khi lấy phiên bản Chrome: {e}")
        return None

def download_chromedriver(version):
    # Trích xuất phiên bản chính (major version)
    major_version = version.split('.')[0]
    
    # URL tải ChromeDriver
    url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
    
    # Lấy phiên bản mới nhất
    latest_version_response = requests.get(url)
    latest_version = latest_version_response.text.strip()
    
    # URL tải file zip
    download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_win32.zip"
    
    # Tải file
    print(f"Đang tải ChromeDriver phiên bản {latest_version}...")
    response = requests.get(download_url)
    
    # Lưu file zip
    with open('chromedriver.zip', 'wb') as f:
        f.write(response.content)
    
    # Giải nén
    with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    
    # Xóa file zip
    os.remove('chromedriver.zip')
    
    # Đặt quyền thực thi
    os.chmod('chromedriver.exe', 0o755)
    
    return os.path.abspath('chromedriver.exe')

def update_settings_json(chromedriver_path):
    settings_path = 'settings.json'
    
    # Đọc file settings
    import json
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    
    # Cập nhật đường dẫn ChromeDriver
    settings['chromedriver_path'] = chromedriver_path
    
    # Ghi lại file settings
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def main():
    # Lấy phiên bản Chrome
    chrome_version = get_chrome_version()
    
    if chrome_version:
        print(f"Phiên bản Chrome hiện tại: {chrome_version}")
        
        # Tải và cài đặt ChromeDriver
        chromedriver_path = download_chromedriver(chrome_version)
        print(f"Đã tải ChromeDriver tại: {chromedriver_path}")
        
        # Cập nhật settings.json
        update_settings_json(chromedriver_path)
        print("Đã cập nhật settings.json với đường dẫn ChromeDriver mới.")
    else:
        print("Không thể xác định phiên bản Chrome.")

if __name__ == "__main__":
    main()
