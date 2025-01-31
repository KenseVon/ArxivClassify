from datetime import datetime
import re
import os
import argparse
from src.model_inference import analyze_paper_relevance, translate_paper_abstract
from src.get_file_from_email import (
    connect_and_login,
    fetch_latest_email,
    get_email_text_body,
    save_email_as_xml,
    close_connection
)
from src.extract_email  import (
    parse_eml,
    extract_papers,
    save_papers_to_json,
    print_paper,
    read_papers_from_json
)
from src.file_writer import json_to_markdown

# 你自己的QQ邮箱账号和授权码（建议从环境变量读取，而不是直接写在代码里）
email_user = "**********@qq.com"
email_pass = "**********"

def get_latest_arxiv_email():
    """
    从指定文件夹获取最新 arXiv 邮件并保存为 XML 文件，返回不带后缀的文件名。
    """
    # 1. 连接并登录
    mail, status = connect_and_login(email_user, email_pass)
    if status != 'OK' or not mail:
        print("登录失败，无法获取邮件。")
        return None
    
    # 2. 获取最新邮件
    folder_name = '&UXZO1mWHTvZZOQ-/arxiv'  # 你自己指定的文件夹，也可以是 'INBOX'
    msg, subject, from_, date_str = fetch_latest_email(mail, folder_name)
    if not msg:
        # 出错或者没有邮件，直接关闭连接退出
        close_connection(mail)
        return None
    
    print("最新邮件：")
    print(f"Subject: {subject}")
    print(f"From: {from_}")
    print(f"Date: {date_str}")
    
    # 3. 获取邮件正文
    body = get_email_text_body(msg)
    
    # 4. 保存为 XML
    filename = save_email_as_xml(subject, from_, date_str, body, output_dir='./downloads')
    print(f"邮件已保存为: {filename}")
    
    # 5. 关闭连接
    close_connection(mail)
    # 返回不带后缀的路径，如 './downloads/<subject>_<date_str>'
    return filename.replace('.xml', '')

def parse_and_extract(filename_base):
    """
    给定不带后缀的文件路径（filename_base），读取 .xml 文件并提取论文信息，然后保存为 .json。
    返回 JSON 文件路径。
    """
    if not filename_base:
        print("未提供有效的 XML 文件，无法解析。")
        return None
    
    xml_path = filename_base + '.xml'
    if not os.path.exists(xml_path):
        print(f"找不到文件: {xml_path}")
        return None
    
    msg = parse_eml(xml_path)
    papers = extract_papers(msg)
    
    json_path = filename_base + '.json'
    save_papers_to_json(papers, json_path)
    print(f"已将论文信息保存到 {json_path}")
    return json_path

def analyze_papers(json_path):
    """
    对 JSON 文件中的论文进行相关性分析，更新后再写回 JSON 文件。
    """
    if not json_path or not os.path.exists(json_path):
        print(f"无法分析，未找到 JSON 文件: {json_path}")
        return None
    
    loaded_papers = read_papers_from_json(json_path)

    for paper in loaded_papers:
        # 如果摘要是只有横线，就跳过
        if re.match(r'^-+$', paper.get('Abstract', '')):
            continue
        
        relevance_result = analyze_paper_relevance(paper)
        paper.update(relevance_result)

    # 将更新完的 paper 词典重新保存到 JSON 文件
    save_papers_to_json(loaded_papers, json_path)
    print(f"已将更新后的论文信息保存到 {json_path}")
    return json_path

def generate_markdown(json_path):
    """
    将 JSON 文件转换为 Markdown 文件保存。
    """
    if not json_path or not os.path.exists(json_path):
        print(f"无法生成 Markdown，未找到 JSON 文件: {json_path}")
        return None
    import datetime
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    md_path = f'/Users/kense/Documents/MyWorld/arxiv/arxiv_{date_str}.md'
    json_to_markdown(json_path, md_path)
    print(f"Markdown 文件已生成: {md_path}")
    return md_path

def main():
    """
    主函数，通过命令行参数实现：
    - --fetch-email  : 是否获取最新 arXiv 邮件并保存为 XML
    - --extract-data : 是否解析（XML -> JSON）
    - --analyze-data : 是否对 JSON 里的论文进行相关性分析
    - --generate-md  : 是否生成 Markdown 文件
    - --file FILE    : 手动指定 .xml 或 .json 文件，以替代获取的新邮件
    - --all         : 执行完整流程（相当于同时使用以上所有选项）
    """
    parser = argparse.ArgumentParser(description="ArXiv论文处理流程")
    parser.add_argument("--fetch-email", action="store_true", help="获取最新邮件并保存为 XML")
    parser.add_argument("--extract-data", action="store_true", help="解析 XML -> JSON")
    parser.add_argument("--analyze-data", action="store_true", help="对 JSON 中的论文进行相关性分析")
    parser.add_argument("--generate-md", action="store_true", help="从 JSON 生成 Markdown 文件")
    parser.add_argument("--file", type=str, default=None, help="手动提供 XML 或 JSON 文件路径（不带后缀也可）")
    parser.add_argument("--all", action="store_true", help="执行完整流程（获取邮件->解析->分析->生成MD）")

    args = parser.parse_args()

    # 如果使用 --all，则设置所有步骤为 True
    if args.all:
        args.fetch_email = True
        args.extract_data = True
        args.analyze_data = True
        args.generate_md = True

    # 用来记录不带后缀的文件路径，比如 ./downloads/xxx
    filename_base = None
    json_path = None

    # 如果传入了 --file，我们需要判断它是 .xml / .json / 或不带后缀
    if args.file:
        # 去掉后缀，以便后续统一处理
        if args.file.endswith('.xml'):
            filename_base = args.file.replace('.xml', '')
        elif args.file.endswith('.json'):
            # 如果是 .json 文件，后面就直接用它做分析或生成 Markdown
            json_path = args.file
            # 可以从中推断 filename_base，但不一定需要
            filename_base = args.file.replace('.json', '')
        else:
            # 可能用户只给了个不带后缀的路径
            filename_base = args.file

    # 1. 获取最新邮件并保存为 XML
    if args.fetch_email:
        temp_filename_base = get_latest_arxiv_email()
        # 如果成功获取邮件，就覆盖 filename_base
        if temp_filename_base:
            filename_base = temp_filename_base

    # 2. 如果需要解析（XML->JSON），就执行
    if args.extract_data:
        if filename_base:
            json_path = parse_and_extract(filename_base)
        else:
            print("无法执行解析，未提供文件且未fetch_email。")

    # 3. 如果需要分析论文
    if args.analyze_data:
        # 如果上一步有生成/更新 json_path，就用它，否则检查有无自定义 json_path
        if not json_path and filename_base:
            # 尝试使用 filename_base.json
            possible_json = filename_base + '.json'
            if os.path.exists(possible_json):
                json_path = possible_json
        
        if json_path:
            json_path = analyze_papers(json_path)
        else:
            print("无法执行分析：未找到可用的 JSON 文件。")

    # 4. 如果需要生成 Markdown
    if args.generate_md:
        # 同样检查是否有 json_path
        if not json_path and filename_base:
            # 尝试 filename_base.json
            possible_json = filename_base + '.json'
            if os.path.exists(possible_json):
                json_path = possible_json
        
        if json_path:
            generate_markdown(json_path)
        else:
            print("无法生成 Markdown：未找到可用的 JSON 文件。")

    # 如果用户什么参数都没传，就提示用法
    if not any([args.fetch_email, args.extract_data, args.analyze_data, args.generate_md, args.all]):
        parser.print_help()

if __name__ == '__main__':
    main()
