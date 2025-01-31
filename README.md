# ArxivClassify



## 📋 项目简介

本项目是一个自动化工具，用于处理从 ArXiv 获取的论文邮件。它支持从邮箱中获取最新的论文邮件，解析邮件内容，分析论文摘要的相关性，并将结果保存为 JSON 和 Markdown 格式，方便进一步查看和管理。

---

## 🚀 功能

- **获取最新邮件**：从指定邮箱文件夹中获取最新的 ArXiv 邮件，并保存为 XML 文件。
- **解析论文信息**：从 XML 文件中提取论文的标题、作者、摘要等信息，并保存为 JSON 格式。
- **相关性分析**：对 JSON 文件中的论文摘要进行分析，标注论文的相关性。
- **生成 Markdown 文件**：将论文信息从 JSON 文件转换为 Markdown 格式，方便查看。

---

## 📂 目录结构

project/
│
├── src/
│   ├── model_inference.py      # 相关性分析和摘要翻译模块
│   ├── get_file_from_email.py  # 从邮箱获取邮件
│   ├── extract_email.py        # 解析邮件内容
│   ├── file_writer.py          # 生成 Markdown 文件
│
├── downloads/                  # 下载的邮件文件和解析结果
│
├── main.py                     # 主脚本
│
└── README.md                   # 项目说明文档

---

## 🛠️ 安装和依赖

### **1. 安装依赖**
请确保你已经安装了必要的 Python 依赖。你可以通过以下命令安装：
```bash
pip install -r requirements.txt

或者，手动安装以下库：

pip install imaplib argparse re os json datetime

🔑 配置邮箱

在 main.py 中，填写你的邮箱账号和授权码：

email_user = "你的邮箱@example.com"
email_pass = "你的邮箱授权码"

确保你的邮箱开启了 IMAP 服务。

📖 使用方法

运行以下命令来执行不同的任务：

1. 获取最新邮件

从邮箱中获取最新的 ArXiv 邮件并保存为 XML 文件：

python main.py --fetch-email

2. 解析 XML 文件

将保存的 XML 文件解析为 JSON 文件：

python main.py --extract-data --file downloads/example.xml

3. 分析论文摘要

对 JSON 文件中的论文摘要进行相关性分析：

python main.py --analyze-data --file downloads/example.json

4. 生成 Markdown 文件

将论文信息从 JSON 文件转换为 Markdown 格式：

python main.py --generate-md --file downloads/example.json

5. 执行完整流程

一键完成获取邮件、解析、分析和生成 Markdown 的完整流程：

python main.py --all

📌 参数说明

参数名	说明
--fetch-email	获取最新邮件并保存为 XML 文件
--extract-data	从 XML 文件解析论文信息并保存为 JSON 文件
--analyze-data	分析 JSON 文件中的论文摘要
--generate-md	将 JSON 文件中的论文信息生成 Markdown 文件
--file <文件路径>	手动指定 XML 或 JSON 文件路径
--all	执行完整流程：获取邮件 → 解析 → 分析 → 生成 MD

🖋️ 输出文件说明
	•	XML 文件：下载的邮件内容（存储在 downloads/ 目录下）。
	•	JSON 文件：从 XML 提取的论文信息。
	•	Markdown 文件：从 JSON 转换而来的 Markdown 格式文件。

⚙️ 常见问题

Q1: 邮箱登录失败怎么办？
	1.	检查你的邮箱账号和授权码是否正确。
	2.	确保邮箱启用了 IMAP 服务。

Q2: 如何修改邮箱文件夹？

在 main.py 中，修改 folder_name 的值：

folder_name = '&UXZO1mWHTvZZOQ-/arxiv'  # 修改为你的文件夹名称

Q3: 如何调试分析问题？

你可以在每个函数中添加调试日志，例如：

print("正在解析邮件内容...")

💡 未来改进
	•	增加对多语言论文摘要的自动翻译支持。
	•	支持从其他邮箱服务（如 Gmail）获取邮件。
	•	提供 Web 界面，方便管理和查看解析结果。

📜 许可证

本项目基于 MIT License。

🤝 贡献

如果你有改进建议或发现任何问题，欢迎提交 Issue 或 Pull Request！

📞 联系

如果你有任何问题，可以通过以下方式联系我：
	•	Email: 你的邮箱@example.com

---

### **保存为 `README.md`**
将上述内容复制到 `README.md` 文件中，并保存。这样，你的项目就有一个清晰、完整的说明文档啦！ 🎉
