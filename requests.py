import http.client
import json
import gzip
import zlib
import urllib.parse

class HttpClient:
    def __init__(self, base_url):
        """Khởi tạo HTTP client với base URL."""
        parsed_url = urllib.parse.urlparse(base_url)
        self.host = parsed_url.netloc
        self.scheme = parsed_url.scheme
        self.conn = self._create_connection()
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        self.cookies = {}

    def _create_connection(self):
        """Tạo kết nối HTTP hoặc HTTPS."""
        if self.scheme == "https":
            return http.client.HTTPSConnection(self.host)
        else:
            return http.client.HTTPConnection(self.host)

    def _handle_response(self, response):
        """Xử lý response, bao gồm giải nén gzip và xử lý cookies."""
        content_encoding = response.getheader("Content-Encoding", "")
        body = response.read()
        
        if "gzip" in content_encoding:
            body = gzip.decompress(body)
        elif "deflate" in content_encoding:
            body = zlib.decompress(body)

        # Cập nhật cookies từ response
        set_cookie = response.getheader("Set-Cookie")
        if set_cookie:
            for cookie in set_cookie.split(";"):
                key_value = cookie.split("=")
                if len(key_value) == 2:
                    self.cookies[key_value[0].strip()] = key_value[1].strip()
        
        return {
            "status_code": response.status,
            "headers": dict(response.getheaders()),
            "body": body.decode("utf-8", errors="ignore"),
        }

    def _make_request(self, method, path, headers=None, body=None):
        """Gửi request với phương thức bất kỳ."""
        headers = headers or {}
        headers.update(self.default_headers)

        # Thêm cookies vào header
        if self.cookies:
            cookie_header = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
            headers["Cookie"] = cookie_header
        
        self.conn.request(method, path, body=body, headers=headers)
        response = self.conn.getresponse()
        return self._handle_response(response)

    def get(self, path, params=None, headers=None):
        """Gửi request GET."""
        if params:
            path += "?" + urllib.parse.urlencode(params)
        return self._make_request("GET", path, headers=headers)

    def post(self, path, data=None, headers=None, json_data=False):
        """Gửi request POST."""
        headers = headers or {}
        body = None

        if json_data and data:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data)
        elif data:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            body = urllib.parse.urlencode(data)

        return self._make_request("POST", path, headers=headers, body=body)

    def close(self):
        """Đóng kết nối."""
        self.conn.close()

# ======= CÁCH SỬ DỤNG =======
client = HttpClient("https://www.example.com")

# Gửi request GET
response = client.get("/")
print(response["status_code"], response["body"][:500])

# Gửi request POST
response = client.post("/submit", data={"key": "value"}, json_data=True)
print(response["status_code"], response["body"])

# Đóng kết nối
client.close()
