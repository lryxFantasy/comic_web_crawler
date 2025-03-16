import os
import re
import aiohttp
import aiofiles  # 引入 aiofiles 库
from selenium import webdriver
from lxml import etree
import time
import asyncio
from PIL import Image


# 获取章节目录
def getCatalog(driver):
    url = input("请输入漫画网址：")
    driver.get(url)  # 加载漫画目录页面

    # 获取页面源代码
    page_source = driver.page_source
    tree = etree.HTML(page_source)

    # XPath 提取章节数据
    result = tree.xpath("/html/body/div[3]/div/div[1]/div[3]/div[2]/@x-data")
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


# 检查图片是否有效
def is_image_valid(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()  # 验证图片是否有效
        return True
    except Exception:
        return False


# 异步下载章节内容
async def download_image(session, url, headers, title, folder_name, retry_count=3):
    try:
        # 提取页码部分
        match = re.search(r'(\d+)-\w+\.jpg', url)
        page_number = match.group(1)

        # 图片保存路径
        image_name = f"{title}_image_{page_number}.jpg"
        image_path = f"{folder_name}\\{image_name}"

        # 检查图片是否已经存在且完整
        if os.path.exists(image_path) and is_image_valid(image_path):
            print(f"图片 {image_name} 已存在且完整，跳过下载")
            return (None, None)  # 跳过该图片

        # 如果图片不存在或文件损坏，进行下载
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                os.makedirs(folder_name, exist_ok=True)
                # 使用 aiofiles 异步写入文件
                async with aiofiles.open(image_path, 'wb') as file:
                    await file.write(await response.content.read())
                print(f"图片 {image_name} 下载成功！")
                return (None, None)  # 下载成功，返回空元组表示无错误
            else:
                print(f"图片 {url} 下载失败，状态码：{response.status}")
                # 如果下载失败，重试
                if retry_count > 0:
                    print(f"正在重试下载图片 {image_name}，剩余重试次数：{retry_count}")
                    return await download_image(session, url, headers, title, folder_name, retry_count - 1)
                else:
                    print(f"图片 {image_name} 下载失败，跳过该图片。")
                    return (image_name, url)  # 返回错误信息
    except Exception as e:
        print(f"下载图片 {url} 时发生错误: {e}")
        if retry_count > 0:
            print(f"正在重试下载图片 {image_name}，剩余重试次数：{retry_count}")
            return await download_image(session, url, headers, title, folder_name, retry_count - 1)
        else:
            print(f"图片 {image_name} 下载失败，跳过该图片。")
            return (image_name, url)  # 返回错误信息


# 异步下载章节内容
async def contentDownload(driver, id, title, error_list):
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
                "Referer": "https://mycomic.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            }
            task = download_image(session, url, headers, title, folder_name)
            tasks.append(task)

        # 并发执行下载任务
        results = await asyncio.gather(*tasks)

        # 将下载失败的图片记录到错误列表中
        for image_name, url in results:
            if image_name:  # 如果 image_name 不为 None，说明下载失败
                error_list.append({"image_name": image_name, "url": url})

    # 刷新当前页面或进行其他清理操作（不关闭浏览器）
    driver.get("about:blank")  # 清空当前页面，避免影响下一个章节下载


# 主程序，获取章节目录并下载每个章节
async def main():
    # 初始化 Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("disable-blink-features=AutomationControlled")  # 核心代码，禁用 blink 特征

    driver = webdriver.Chrome(options=options)

    # 获取章节目录
    catalog = getCatalog(driver)

    # 存储所有下载失败的图片信息
    error_list = []

    # 异步下载每个章节的内容
    tasks = []
    for chapter in catalog:
        # 对每个章节调用异步下载函数
        tasks.append(contentDownload(driver, chapter["id"], chapter["title"], error_list))

    # 等待所有任务完成
    await asyncio.gather(*tasks)

    # 关闭 WebDriver
    driver.quit()

    # 输出所有下载失败的图片信息
    if error_list:
        print("\n下载失败的图片：")
        for error in error_list:
            print(f"图片名称: {error['image_name']}, URL: {error['url']}")

    else:
        print("\n所有图片下载成功！")


if __name__ == '__main__':
    t1 = time.time()
    asyncio.run(main())
    t2 = time.time()
    print(f"下载完成！总共花费时间: {t2 - t1}秒")
