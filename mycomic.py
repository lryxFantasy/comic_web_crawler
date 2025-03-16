import os
import re
import aiohttp
from selenium import webdriver
from lxml import etree
import time
import asyncio


# 获取章节目录
def getCatalog(driver):
    url = input("请输入漫画网址：")
    driver.get(url)  # 加载漫画目录页面

    # 获取页面源代码
    page_source = driver.page_source
    tree = etree.HTML(page_source)

    # XPath 提取章节数据
    result = tree.xpath("/html/body/div[3]/div/div[1]/div[3]/div[1]/@x-data")
    chapters = result[0]

    # 正则表达式匹配章节信息
    obj = re.compile(r'{\"id\":(?P<id>\d+),\"title\":\"(?P<title>[^\"]+)\"}', re.S)
    result = obj.finditer(chapters)

    menu_list = []
    for it in result:
        id = it.group("id")
        title = it.group("title")
        # 将 Unicode 转换为可读的字符串
        title = title.encode('utf-8').decode('unicode_escape')

        # 将数据存储到字典中
        data = {
            "id": id,
            "title": title
        }

        # 将字典添加到列表中
        menu_list.append(data)

    # 打印章节目录列表
    print(menu_list)

    return menu_list


# 异步下载章节内容
async def download_image(session, url, headers, title, folder_name):
    try:
        match = re.search(r'(\d+)-\w+\.jpg', url)
        page_number = match.group(1)  # 提取页码部分
        # 发送异步 GET 请求并携带自定义请求头
        async with session.get(url, headers=headers) as response:
            # 如果请求成功
            if response.status == 200:
                # 图片保存路径，使用章节标题和索引作为文件名，避免文件名重复
                image_name = f"{title}_image_{page_number}.jpg"
                # 确保保存目录存在
                os.makedirs(folder_name, exist_ok=True)
                # 直接将字节数据写入文件
                with open(f"{folder_name}\\{image_name}", 'wb') as file:
                    file.write(await response.content.read())
                print(f"图片 {image_name} 下载成功！")
            elif response.status == 304:
                print(f"图片 {url} 未修改，无需下载")
            else:
                print(f"图片 {url} 下载失败，状态码：{response.status}")
    except Exception as e:
        print(f"下载图片 {url} 时发生错误: {e}")


# 异步下载章节内容
async def contentDownload(driver, id, title):
    driver.get(f"https://mycomic.com/chapters/{id}")  # 加载章节页面

    # 获取页面源代码
    page_source = driver.page_source
    tree = etree.HTML(page_source)

    # 提取所有 img 标签的 src 属性
    result = tree.xpath("/html/body/div[3]/div/div[2]/img/@src| /html/body/div[3]/div/div[2]/img/@data-src")

    # 使用 set 去重
    unique_urls = set(result)

    # 创建一个文件夹，以章节标题命名
    folder_name = f"manga\\{title}"

    # 使用 aiohttp 进行异步请求
    async with aiohttp.ClientSession() as session:
        # 创建并发下载任务
        tasks = []
        for url in unique_urls:
            headers = {
                "Referer": "https://hommec.com/chapters/797592/1-9582f8.jpg",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            }
            tasks.append(download_image(session, url, headers, title, folder_name))

        # 并发执行下载任务
        await asyncio.gather(*tasks)

    # 刷新当前页面或进行其他清理操作（不关闭浏览器）
    driver.get("about:blank")  # 清空当前页面，避免影响下一个章节下载


# 主程序，获取章节目录并下载每个章节
async def main():
    # 初始化 Selenium WebDriver
    driver = webdriver.Chrome()

    # 获取章节目录
    catalog = getCatalog(driver)

    # 异步下载每个章节的内容
    tasks = []
    for chapter in catalog:
        # 对每个章节调用异步下载函数
        tasks.append(contentDownload(driver, chapter["id"], chapter["title"]))

    # 等待所有任务完成
    await asyncio.gather(*tasks)

    # 关闭 WebDriver
    driver.quit()


if __name__ == '__main__':
    t1 = time.time()
    asyncio.run(main())
    t2 = time.time()
    print(f"下载完成！总共花费时间: {t2 - t1}秒")
