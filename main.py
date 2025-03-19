from requests import HttpClient

class HTMLParserHelper:
    """Hỗ trợ phân tích HTML để lấy link theo điều kiện."""

    @staticmethod
    def extract_first_apk_link(html_data):
        """Lấy link từ <a class='accent_color'> có chứa 'APK'."""
        from html.parser import HTMLParser

        class APKLinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.found_link = None
                self.capture_text = False
                self.current_link = None

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    attrs_dict = dict(attrs)
                    if "class" in attrs_dict and "accent_color" in attrs_dict["class"]:
                        self.current_link = attrs_dict["href"]
                        self.capture_text = True  

            def handle_data(self, data):
                if self.capture_text and "APK" in data and not self.found_link:
                    self.found_link = self.current_link  

            def handle_endtag(self, tag):
                if tag == "a":
                    self.capture_text = False
                    self.current_link = None

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
                    href = attrs_dict.get("href", "")
                    if "key=" in href:
                        self.found_link = href

        parser = KeyLinkParser()
        parser.feed(html_data)
        return parser.found_link


# ========== KẾT NỐI & TẢI DỮ LIỆU ==========
client = HttpClient("https://www.apkmirror.com")

# Bước 1: Lấy link đầu tiên từ <a class="accent_color"> chứa "APK"
response = client.get("/apk/google-inc/youtube/youtube-19-44-39-release/")
if response["status_code"] == 200:
    apk_link = HTMLParserHelper.extract_first_apk_link(response["body"])
    if apk_link:
        print("Link APK:", apk_link)
    else:
        print("Không tìm thấy link APK.")
        client.close()
        exit()
else:
    print("Không thể tải trang, mã lỗi:", response["status_code"])
    client.close()
    exit()

# Bước 2: Lấy HTML từ link APK và tìm link chứa "key="
response = client.get(apk_link)
if response["status_code"] == 200:
    key_link1 = HTMLParserHelper.extract_first_key_link(response["body"])
    if key_link1:
        print("Link chứa 'key=' (lần 1):", key_link1)
    else:
        print("Không tìm thấy link chứa 'key=' lần 1.")
        client.close()
        exit()
else:
    print("Không thể tải trang, mã lỗi:", response["status_code"])
    client.close()
    exit()

# Bước 3: Lấy HTML từ link "key=" lần 1 và tìm link "key=" lần 2
response = client.get(key_link1)
if response["status_code"] == 200:
    key_link2 = HTMLParserHelper.extract_first_key_link(response["body"])
    if key_link2:
        print("Link chứa 'key=' (lần 2):", key_link2)
    else:
        print("Không tìm thấy link chứa 'key=' lần 2.")
        client.close()
        exit()
else:
    print("Không thể tải trang, mã lỗi:", response["status_code"])
    client.close()
    exit()

# Bước 4: Tải file từ link "key=" lần 2
response = client.get(key_link2)
if response["status_code"] == 200:
    with open("youtube-v.19.44.39.apk", "wb") as f:
        f.write(response["body"])
    print("File đã được tải xuống thành công: youtube-v.19.44.39.apk")
else:
    print("Không thể tải file, mã lỗi:", response["status_code"])

# Đóng kết nối
client.close()