import os


def get_non_epub_files(folder_path):
    """获取所有非EPUB文件列表"""
    to_delete = []
    for foldername, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if not filename.lower().endswith('.epub'):
                file_path = os.path.join(foldername, filename)
                to_delete.append(file_path)
    return to_delete


def delete_files(file_list):
    """执行删除操作并返回统计结果"""
    deleted_count = 0
    error_count = 0
    for file_path in file_list:
        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"已删除：{file_path}")
        except Exception as e:
            error_count += 1
            print(f"删除失败 [{file_path}]: {str(e)}")
    return deleted_count, error_count


def display_preview(file_list, max_preview=10):
    """显示将要删除的文件预览"""
    print(f"\n发现 {len(file_list)} 个非EPUB文件：")
    # 显示前10个文件
    for idx, file_path in enumerate(file_list[:max_preview]):
        print(f"[{idx + 1}] {file_path}")
    if len(file_list) > max_preview:
        print(f"......（只显示前{max_preview}个文件）")


if __name__ == "__main__":
    # 获取文件夹路径
    target_folder = r"D:\Fantasy文件夹\大学新生资料\各种资料\编程\web_crawler\spider10-comic\manga"
    while not os.path.isdir(target_folder):
        print(f"\n错误：文件夹不存在或路径无效 '{target_folder}'")
        target_folder = input("请重新输入有效的文件夹路径（或按Ctrl+C退出）：").strip().strip('"')

    # 获取待删除文件列表
    delete_list = get_non_epub_files(target_folder)

    if not delete_list:
        print("\n该文件夹中没有需要删除的非EPUB文件")
        sys.exit(0)

    # 显示预览
    display_preview(delete_list)

    # 二次确认
    print("\n警告：以上文件将被永久删除！")
    confirmation = input("是否确认删除？(y/N): ").strip().lower()

    if confirmation == 'y':
        # 执行删除
        print("\n开始删除操作...")
        deleted, errors = delete_files(delete_list)

        # 输出结果
        print("\n操作完成")
        print(f"成功删除文件数：{deleted}")
        print(f"删除失败数：{errors}")
    else:
        print("操作已取消")