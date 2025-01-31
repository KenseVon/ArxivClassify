import json
import requests
from requests.exceptions import RequestException, Timeout
import re

def fix_invalid_escapes(s: str) -> str:
    # 只允许 \" \\ \/ \b \f \n \r \t 等合法转义
    # 其它情况一律替换成 \\x
    return re.sub(r'\\(?![\"\\/bfnrt])', r'\\\\', s)


def analyze_paper_relevance(paper):
    # 检查输入
    if 'Abstract' not in paper:
        return {"error": "No abstract found in the paper"}

    # 构建提示词
    prompt = f"""请分析以下论文摘要，首先判断该论文是否与星际介质相关，如果与星际介质不相关再进一步判断是否与恒星形成活动相关，如果与星际介质相关则优先返回'ISM'，如果与恒星形成活动相关则返回'StarFormation'，如果与两者都不相关则返回'Other'。然后再返回3到5个英文关键词和其对应的中文翻译。
    摘要内容: {paper['Abstract']}
    请严格输出 JSON，不要添加任何额外注释或文本。    
    请按照以下JSON格式返回:
    {{
        "Type": ISM/StarFormation/Other,
        "keywords": ["英文关键词1", "英文关键词2", "英文关键词3"...],
        "keywords_CN": ["中文关键词1", "中文关键词2", "中文关键词3"...]
    }}
    """
    
    try:
        # 调用大模型
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
            timeout=300  # 设置请求超时
        )
        
        # 检查响应状态
        response.raise_for_status()

        # 4. 获取大模型的原始输出
        raw_result = response.json().get("response", "")
        if not raw_result:
            return {"error": "No valid response from the model"}
        
        print(f"模型原始输出:\n{raw_result}")
        
        # 5. 尝试解析为 JSON
        raw_output = raw_result  # 从大模型拿到的字符串

        # 在 json.loads 前先进行修正
        cleaned_output = fix_invalid_escapes(raw_output)
        
        try:
            result_dict = json.loads(cleaned_output.split("```json")[1].split("```")[0])
            summary = cleaned_output.split("```json")[0]
        except json.JSONDecodeError as je:
            # 如果出现 JSON 解析错误，则返回错误提示
            print(f"Failed to parse JSON response: {je}")
            return raw_result, cleaned_output

        # 6. 提取字段并做简单检查
        Type = result_dict["Type"]
        keywords = result_dict["keywords"]
        keywords_CN = result_dict["keywords_CN"]
        # 如果想严格控制关键词数量，可以在此检查长度
        # if not (3 <= len(keywords_cn) <= 5):
        #     return {"error": f"Keywords count is not in the range [3..5], got {len(keywords_cn)}"}

        # 7. 返回结构化数据
        return {
            "Type": Type,
            "keywords": keywords,
            "keywords_CN": keywords_CN,
            "summary": summary
        }
        
    except RequestException as e:
        # 网络请求相关异常
        return {"error": f"Request failed: {e}"}
    except Timeout:
        # 超时异常
        return {"error": "The request timed out"}
    except Exception as e:
        # 其他未知异常
        return {"error": f"An unexpected error occurred: {e}"}



def translate_paper_abstract(paper):
    # 1. 检查输入
    if 'Abstract' not in paper:
        return {"error": "No abstract found in the paper"}
    
    # 2. 构建 Prompt
    prompt = f"""请将以下论文摘要翻译成中文。也给出3-5个中文关键词。
    摘要内容: {paper['Abstract']}
    请严格输出 JSON，不要添加任何额外注释或文本。
    请按照以下JSON格式返回:
    {{
        "Abstract_CN": "中文翻译内容",
        "keywords_CN": ["关键词1", "关键词2", "关键词3"...]
    }}
    """
    
    try:
        # 3. 调用大模型
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json={
                "model": "deepseek-r1:14b",
                "prompt": prompt,
                "stream": False
            },
            timeout=300  # 设置请求超时
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 4. 获取大模型的原始输出
        raw_result = response.json().get("response", "")
        if not raw_result:
            return {"error": "No valid response from the model"}
        
        print(f"模型原始输出:\n{raw_result}")
        
        # 5. 尝试解析为 JSON
        raw_output = raw_result  # 从大模型拿到的字符串

        # 在 json.loads 前先进行修正
        cleaned_output = fix_invalid_escapes(raw_output)
        
        try:
            result_dict = json.loads(cleaned_output.split("```json")[1].split("```")[0])
        except json.JSONDecodeError as je:
            # 如果出现 JSON 解析错误，则返回错误提示
            print(f"Failed to parse JSON response: {je}")
            return raw_result, cleaned_output
        
        # 6. 提取字段并做简单检查
        abstract_cn = result_dict.get("Abstract_CN", "").strip()
        keywords_cn = result_dict.get("keywords_CN", [])

        # 如果想严格控制关键词数量，可以在此检查长度
        # if not (3 <= len(keywords_cn) <= 5):
        #     return {"error": f"Keywords count is not in the range [3..5], got {len(keywords_cn)}"}

        # 7. 返回结构化数据
        return {
            "Abstract_CN": abstract_cn,
            "keywords_CN": keywords_cn
        }
        
    except RequestException as e:
        # 网络请求相关异常
        return {"error": f"Request failed: {e}"}
    except Timeout:
        # 超时异常
        return {"error": "The request timed out"}
    except Exception as e:
        # 其他未知异常
        return {"error": f"An unexpected error occurred: {e}"}
