import os
import sys
from PyPDF2 import PdfMerger

def get_pdf_files(folder_path, sort_by='name'):
    """
    获取文件夹中的PDF文件列表
    :param folder_path: 文件夹路径
    :param sort_by: 排序方式 ['name', 'mtime', 'ctime']
    :return: 排序后的PDF文件路径列表
    """
    pdf_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            pdf_files.append(file_path)

    # 根据指定方式排序
    if sort_by == 'mtime':
        pdf_files.sort(key=lambda x: os.path.getmtime(x))
    elif sort_by == 'ctime':
        pdf_files.sort(key=lambda x: os.path.getctime(x))
    else:  # 默认按文件名排序
        pdf_files.sort()

    return pdf_files

def merge_pdfs(pdf_files, output_path):
    """
    合并PDF文件
    :param pdf_files: 要合并的PDF文件路径列表
    :param output_path: 输出文件路径
    :return: (总页数, 合并文件数)
    """
    merger = PdfMerger()
    total_pages = 0
    merged_files = 0

    for pdf_file in pdf_files:
        try:
            with open(pdf_file, 'rb') as f:
                merger.append(f)
                pages = len(merger.pages)
                added_pages = pages - total_pages
                total_pages = pages
                merged_files += 1
                print(f"已添加：{os.path.basename(pdf_file)} ({added_pages}页)")
        except Exception as e:
            print(f"跳过文件 [{pdf_file}]: {str(e)}")

    with open(output_path, 'wb') as f:
        merger.write(f)

    return total_pages, merged_files

def main():
    # 获取文件夹路径
    folder_path = input("请输入包含PDF的文件夹路径：").strip().strip('"')
    while not os.path.isdir(folder_path):
        print(f"\n错误：文件夹不存在 '{folder_path}'")
        folder_path = input("请重新输入有效路径（或按Ctrl+C退出）：").strip().strip('"')

    # 选择排序方式
    print("\n请选择排序方式：")
    print("1. 按文件名排序（默认）")
    print("2. 按修改时间排序")
    print("3. 按创建时间排序")
    sort_choice = input("请输入选择 [1-3] (默认1)：").strip() or '1'

    sort_options = {'1': 'name', '2': 'mtime', '3': 'ctime'}
    sort_by = sort_options.get(sort_choice, 'name')

    # 获取PDF文件列表
    pdf_files = get_pdf_files(folder_path, sort_by)
    if not pdf_files:
        print("\n该文件夹中没有PDF文件")
        sys.exit(0)

    # 显示文件列表
    print("\n将按以下顺序合并PDF文件：")
    for idx, file_path in enumerate(pdf_files, 1):
        print(f"{idx}. {os.path.basename(file_path)}")

    # 确认继续
    confirmation = input("\n是否继续合并？(y/N): ").strip().lower()
    if confirmation == 'n':
        print("操作已取消")
        sys.exit(0)

    # 设置输出路径
    default_output = os.path.join(folder_path, "merged.pdf")
    output_path = input(f"请输入输出文件名（默认：{default_output}）：").strip().strip('"') or default_output

    # 执行合并
    print("\n开始合并PDF文件...")
    total_pages, merged_files = merge_pdfs(pdf_files, output_path)

    # 显示结果
    print("\n合并完成！")
    print(f"成功合并文件数：{merged_files}/{len(pdf_files)}")
    print(f"总页数：{total_pages}")
    print(f"输出文件：{output_path}")

if __name__ == "__main__":
    main()