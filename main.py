from requests import HttpClient

class HTMLParserHelper:
    """Hỗ trợ phân tích HTML để lấy link theo điều kiện."""

    @staticmethod
    def extract_apk_link(html_data):
        """Lấy link từ <a class='accent_color'> có 'android-apk-download/' ở cuối và 'APK' gần nhất phía sau."""
        from html.parser import HTMLParser

        class APKLinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.last_valid_link = None
                self.found_link = None  

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    attrs_dict = dict(attrs)
                    href = attrs_dict.get("href")
                    if href and href.endswith("android-apk-download/"):
                        self.last_valid_link = href  

            def handle_data(self, data):
                if "APK" in data and self.last_valid_link and not self.found_link:
                    self.found_link = self.last_valid_link  

        parser = APKLinkParser()
        parser.feed(html_data)
        return parser.found_link

    @staticmethod
    def extract_first_key_link(html_data):
        """Lấy link đầu tiên có href chứa 'key='."""
        from html.parser import HTMLParser

        class KeyLinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.found_link = None

            def handle_starttag(self, tag, attrs):
                if tag == "a" and not self.found_link:
                    attrs_dict = dict(attrs)
                    href = attrs_dict.get("href")
                    if href and "key=" in href:
                        self.found_link = href

        parser = KeyLinkParser()
        parser.feed(html_data)
        return parser.found_link


def handle_redirects(client, url, headers, max_redirects=5):
    """Tự động xử lý redirect 307, 302 để lấy URL cuối cùng."""
    for _ in range(max_redirects):
        response = client.get(url, headers=headers)
        if response["status_code"] in (301, 302, 307):  # Nếu bị redirect
            url = response["headers"].get("Location")  # Lấy URL mới
            if not url:
                break
        else:
            return response  # Trả về response khi không còn redirect
    return None  # Quá số lần redirect mà vẫn lỗi


# ========== KẾT NỐI & TẢI DỮ LIỆU ==========
client = HttpClient("https://www.apkmirror.com")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.apkmirror.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

# Bước 1: Lấy link APK
response = client.get("/apk/google-inc/youtube/youtube-19-44-39-release/", headers=headers)
if response["status_code"] == 200:
    apk_link = HTMLParserHelper.extract_apk_link(response["body"])
    if apk_link:
        print("🔹 Link APK:", apk_link)
    else:
        print("❌ Không tìm thấy link APK.")
        client.close()
        exit()
else:
    print("❌ Không thể tải trang, mã lỗi:", response["status_code"])
    client.close()
    exit()

# Bước 2: Lấy HTML từ link APK và tìm link chứa "key="
response = client.get(apk_link, headers=headers)
if response["status_code"] == 200:
    key_link1 = HTMLParserHelper.extract_first_key_link(response["body"])
    if key_link1:
        print("🔹 Link chứa 'key=' (lần 1):", key_link1)
    else:
        print("❌ Không tìm thấy link chứa 'key=' lần 1.")
        client.close()
        exit()
else:
    print("❌ Không thể tải trang, mã lỗi:", response["status_code"])
    client.close()
    exit()

# Bước 3: Lấy HTML từ link "key=" lần 1 và tìm link "key=" lần 2
response = handle_redirects(client, key_link1, headers)
if response and response["status_code"] == 200:
    key_link2 = HTMLParserHelper.extract_first_key_link(response["body"])
    if key_link2:
        print("🔹 Link chứa 'key=' (lần 2):", key_link2)
    else:
        print("❌ Không tìm thấy link chứa 'key=' lần 2.")
        client.close()
        exit()
else:
    print("❌ Không thể tải trang, mã lỗi:", response["status_code"] if response else "Redirect quá nhiều lần")
    client.close()
    exit()

# Bước 4: Tải file từ link "key=" lần 2
response = handle_redirects(client, key_link2, headers)
if response and response["status_code"] == 200:
    file_name = "youtube-v.19.44.39.apk"
    with open(file_name, "wb") as f:
        f.write(response["body"])
    print(f"✅ File đã được tải xuống thành công: {file_name}")
else:
    print("❌ Không thể tải file, mã lỗi:", response["status_code"] if response else "Redirect quá nhiều lần")

# Đóng kết nối
client.close()