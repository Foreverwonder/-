import os
import sys
from PyQt5.QtWidgets import QApplication

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 加载样式表
    try:
        style_path = os.path.join(current_dir, 'gui', 'styles', 'main.qss')
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"加载样式表失败: {e}")
    
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main()) 