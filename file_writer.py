import json
import re
from collections import defaultdict

def json_to_markdown(json_file_path, md_file_path):
    """
    将 JSON 文件转换为 Markdown，并按 `type` 进行分类存储。
    - 先按 `type` 进行分组，每类论文用一级标题 `# Type: <类型>` 进行区分。
    - 论文内部用二级标题 `## Paper ID: <id>` 标识。
    - 去掉摘要中的换行符，使其变成单行。
    """
    # 1. 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)  # 假设是一个列表结构
    
    # 2. 先按 `type` 进行分类
    categorized_papers = defaultdict(list)
    for paper in papers:
        paper_type = paper.get('Type', 'Unknown')  # 以 'Unknown' 作为默认分类
        categorized_papers[paper_type].append(paper)

    # 3. 定义类型顺序
    type_order = ['ISM', 'StarFormation', 'Other', 'Unknown']

    # 4. 打开 Markdown 文件，按指定顺序写入
    with open(md_file_path, 'w', encoding='utf-8') as f:
        for paper_type in type_order:
            if paper_type in categorized_papers:
                # 一级标题（论文类别）
                f.write(f"# Type: {paper_type}\n\n")
                
                for paper in categorized_papers[paper_type]:
                    # 读取字段，避免 KeyError
                    paper_id = paper.get('id', 'N/A')
                    date = paper.get('date', 'N/A')
                    title = paper.get('Title', 'N/A')
                    authors = paper.get('Authors', 'N/A')
                    summary = paper.get('summary', 'N/A')
                    keywords = paper.get('keywords', 'N/A')
                    keywords_CN = paper.get('keywords_CN', 'N/A')
                    # 摘要换行转换（去掉多余空白字符）
                    abstract = paper.get('Abstract', 'N/A')
                    # 检查是否以两个%开始
                    if abstract.startswith('%%'):
                        abstract_singleline = 'N/A'
                    else:
                        abstract_singleline = abstract.replace('\n', ' ')  # 只替换换行符
                        abstract_singleline = abstract_singleline.replace('&', '\\')  # 替换 `&` 为 `\`

                    # 论文内容（使用二级标题 `##` 进行分隔）
                    f.write(f"\n### **{title}** \n\n")
                    f.write(f"Paper Link: https://arxiv.org/abs/{paper_id} \n")
                    f.write(f"Date: {date}\n\n")
                    f.write("**Keywords**: ")
                    if isinstance(keywords, list):
                        for keyword in keywords:
                            # 将关键词中的空格替换为下划线
                            keyword = keyword.replace(' ', '_')
                            f.write(f"#{keyword} ")
                    f.write("\n")
                    if isinstance(keywords_CN, list):
                        for keyword_CN in keywords_CN:
                            f.write(f" **{keyword_CN}**  ")
                    f.write("\n\n")
                    f.write(f"**Authors**: {authors}\n\n")
                    f.write(f"**Abstract**: {abstract_singleline}\n\n")
                    f.write(f"**Summary**: \n ``` \n{summary}\n ```\n")
                    f.write("---\n\n")  # 每篇论文之间插入分割线

    print(f"已将 {json_file_path} 转换为 Markdown 文件，并按 `type` 分类存入：{md_file_path}")