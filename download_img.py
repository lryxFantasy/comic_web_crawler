import requests
import shutil

# 图片的URL
url = "https://biccam.com/chapters/21988/46-efd6ec.jpg"


# 定义请求头，添加 referer 和 user-agent
headers = {
    "Referer": "https://mycomic.com/",
}

response = requests.get(url, headers=headers, stream=True)

# 如果请求成功
if response.status_code == 200:
    # 打开一个文件来保存图片
    with open("第09卷_image_88.jpg", 'wb') as file:
        # 将图片内容写入文件
        shutil.copyfileobj(response.raw, file)
    print("图片下载成功！")
elif response.status_code == 304:
    print("图片未修改，无需下载")
else:
    print(f"图片下载失败，状态码：{response.status_code}")