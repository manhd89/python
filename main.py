from requests import HttpClient

# Khởi tạo client với trang web đích
client = HttpClient("https://www.apkmirror.com")

# Gửi request GET
response = client.get("/apk/google-inc/youtube-music/youtube-music-8-10-51-release/")

# In kết quả
print("Status Code:", response["status_code"])
print("HTML:", response["body"][:500])

# Đóng kết nối
client.close()
