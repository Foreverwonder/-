安装命令：

1. 首先创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

注意：
- 如果遇到 PyQt5 安装问题，可以尝试：`pip install PyQt5-sip` 先安装 sip
- 在 Linux 系统上可能需要额外安装 Qt 依赖：`sudo apt-get install python3-pyqt5`
- tkinterdnd2 在某些平台可能安装失败，这不影响核心功能使用

运行程序：
```bash
python main.py
```
