import os
from PIL import Image
import img2pdf
from natsort import natsorted


def validate_image(filepath):
    """验证图片是否完整"""
    try:
        with Image.open(filepath) as img:
            img.verify()  # 仅验证图片，不加载图像数据
        return True
    except (IOError, SyntaxError, OSError) as e:
        print(f"❌ 图片加载失败：{filepath} 错误信息: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误：{filepath} 错误信息: {e}")
        return False


def process_chapter(chapter_path, root_folder):
    """处理单个章节"""
    # 检查图片文件
    image_files = []
    broken_images = []

    # 获取所有图片文件
    for f in os.listdir(chapter_path):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(chapter_path, f)
            print(f"正在检查图片：{full_path}")  # 添加调试信息
            if not validate_image(full_path):
                broken_images.append(f)
                continue  # 跳过损坏的图片
            else:
                image_files.append(full_path)

    # 自然排序
    image_files = natsorted(image_files)

    if broken_images:
        print(f"\n⚠️ 发现损坏图片（共 {len(broken_images)} 张）：")
        for img in broken_images:
            print(f"   - {img}")

    # 生成PDF
    pdf_name = f"{os.path.basename(chapter_path)}.pdf"
    output_path = os.path.join(root_folder, pdf_name)

    try:
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(image_files))
        print(f"✅ 已生成：{pdf_name}（{len(image_files)} 页）")
        return True
    except Exception as e:
        print(f"❌ 生成失败：{str(e)}")
        return False


def main():
    print("📚 漫画图片转PDF工具")
    print("=" * 40)

    while True:
        # 获取有效路径
        folder = r"D:\Fantasy文件夹\大学新生资料\各种资料\编程\web_crawler\spider10-comic\manga"
        if not os.path.exists(folder):
            print("❌ 路径不存在，请重新输入")
            continue

        # 遍历子目录
        total_chapters = 0
        success_count = 0

        for item in os.listdir(folder):
            chapter_path = os.path.join(folder, item)
            if os.path.isdir(chapter_path):
                total_chapters += 1
                print(f"\n正在处理章节：{item}")
                if process_chapter(chapter_path, folder):
                    success_count += 1

        print("\n" + "=" * 40)
        print(f"处理完成：共 {total_chapters} 个章节")
        print(f"成功生成：{success_count} 个PDF")
        print(f"失败章节：{total_chapters - success_count} 个")
        break


if __name__ == "__main__":
    main()
