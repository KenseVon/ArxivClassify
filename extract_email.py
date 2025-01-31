import re
import json
from email import policy
from email.parser import BytesParser

def parse_eml(file_path):
    with open(file_path, 'rb') as f:
        return BytesParser(policy=policy.default).parse(f)

def split_entries(body):
    """
    根据特定分隔符拆分正文，返回一个列表，每个元素就是一个“论文条目”字符串。
    """
    return body.split('\n\\\\\na')

def parse_entry(entry):
    """
    解析单个论文条目，返回一个 dict 包含论文字段。
    """
    paper = {}
    lines = entry.split('\n')
    paper_content = []
    is_collecting = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('rXiv:'):
            paper['id'] = line.split(':', 1)[1].strip()
        elif line.startswith('Date:'):
            # 去掉多余字符，比如 (v1) 之类
            date_str = re.sub(r'Date:| \(.*\)', '', line).strip()
            paper['date'] = date_str
        elif line.startswith('Title:'):
            paper['Title'] = line.split(':', 1)[1].strip()
        elif line.startswith('Authors:'):
            paper['Authors'] = line.split(':', 1)[1].strip()
        elif line.startswith('%%--'):
            break
        elif line.startswith('\\\\'):
            # 切换收集摘要的状态
            if is_collecting:
                break
            else:
                is_collecting = True
        elif is_collecting:
            paper_content.append(line)
    
    paper['Abstract'] = '\n'.join(paper_content).strip()
    return paper

def extract_papers(msg):
    papers = []
    body = msg.get_body(preferencelist=('plain')).get_content()
    entries = split_entries(body)
    
    for entry in entries:
        if entry.startswith('rXiv:'):
            paper = parse_entry(entry)
            papers.append(paper)
    return papers

def save_papers_to_json(papers, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=4)

def read_papers_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_papers_as_dict(papers):
    return {paper.get('id', f"Unknown_{idx}"): paper for idx, paper in enumerate(papers)}

def print_paper(papers):
    for paper in papers:
        print(f"arXiv ID: {paper.get('id', 'N/A')}")
        print(f"Date: {paper.get('date', 'N/A')}")
        print(f"Title: {paper.get('Title', 'N/A')}")
        print(f"Authors: {paper.get('Authors', 'N/A')}")
        print(f"Abstract: {paper.get('Abstract', '')}")
        print('-' * 80)