from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QLineEdit, QPushButton, QTextEdit, QMessageBox,
                           QHBoxLayout, QLabel)
from PyQt5.QtCore import (Qt, QTimer, QThread, pyqtSignal, QPoint,
                         QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, 
                         QParallelAnimationGroup, pyqtProperty)
from PyQt5.QtGui import QFont, QEnterEvent, QMouseEvent, QColor, QPainter, QTransform
from .api_client import CozeAPIClient
from .particles import ParticleEffect
from .taiji import TaijiWidget

class AnimatedTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self._scale = 1.0
        self._rotation = 0.0
        self.setStyleSheet("background-color: transparent;")

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = float(value)
        self.update()

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = float(value)
        self.update()

    @pyqtProperty(float)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = float(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 保存当前状态
        painter.save()
        
        # 应用变换
        transform = QTransform()
        transform.translate(self.width()/2, self.height()/2)
        transform.rotate(self._rotation)
        transform.scale(self._scale, self._scale)
        transform.translate(-self.width()/2, -self.height()/2)
        painter.setTransform(transform)
        
        # 设置透明度
        painter.setOpacity(self._opacity)
        
        # 绘制背景
        if self._opacity > 0:
            painter.fillRect(self.viewport().rect(), QColor(44, 24, 16, int(40 * self._opacity)))
            
            # 绘制边框
            painter.setPen(QColor(212, 175, 55, int(255 * self._opacity)))
            painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 19, 19)
        
        # 恢复状态
        painter.restore()
        
        # 设置文本颜色
        self.document().setDefaultStyleSheet(f"color: rgba(212, 175, 55, {int(self._opacity * 255)})")
        
        # 调用原始的绘制方法
        super().paintEvent(event)

class DivinationThread(QThread):
    finished = pyqtSignal(str, bool)
    
    def __init__(self, api_client, question):
        super().__init__()
        self.api_client = api_client
        self.question = question
        
    def run(self):
        result, success = self.api_client.get_divination(self.question)
        self.finished.emit(result, success)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.api_client = CozeAPIClient()
        self.divination_thread = None
        self._drag_pos = None
        self.result_animation = None
        
    def init_ui(self):
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置窗口基本属性
        self.setWindowTitle('易学决策分析')
        self.setMinimumSize(800, 600)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(50)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # 添加标题文本
        title_label = QLabel("易学决策分析")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        # 添加关闭按钮
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        # 添加标题栏到主布局
        main_layout.addWidget(title_bar)
        
        # 创建内容容器
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建输入框
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("请输入您希望从易学获取决策建议的事情...")
        self.question_input.setObjectName("questionInput")
        self.question_input.returnPressed.connect(self.on_divine_clicked)
        
        # 创建起卦按钮
        self.divine_button = QPushButton("起卦")
        self.divine_button.setObjectName("divineButton")
        self.divine_button.clicked.connect(self.on_divine_clicked)
        
        # 创建结果显示区域
        self.result_display = AnimatedTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setObjectName("resultDisplay")
        self.result_display.opacity = 1.0  # 使用属性而不是方法
        
        # 添加部件到内容布局
        content_layout.addWidget(self.question_input)
        content_layout.addWidget(self.divine_button)
        content_layout.addWidget(self.result_display)
        
        # 添加内容容器到主布局
        main_layout.addWidget(content_widget)
        
        # 添加粒子效果
        self.particle_effect = ParticleEffect(self)
        self.particle_effect.resize(self.size())  # 设置粒子效果大小
        self.particle_effect.hide()  # 初始隐藏
        
        # 添加太极图效果
        self.taiji_widget = TaijiWidget(self)
        self.taiji_widget.hide()  # 初始隐藏
        
        # 设置动画计时器
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_dots = 0
        
    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        if hasattr(self, 'particle_effect'):
            self.particle_effect.resize(self.size())
        if hasattr(self, 'taiji_widget'):
            x = (self.width() - self.taiji_widget.width()) // 2
            y = (self.height() - self.taiji_widget.height()) // 2
            self.taiji_widget.move(x, y)
            
    def showEvent(self, event):
        """处理窗口显示事件"""
        super().showEvent(event)
        # 确保粒子效果覆盖整个窗口
        if hasattr(self, 'particle_effect'):
            self.particle_effect.resize(self.size())
    
    def mousePressEvent(self, event: QMouseEvent):
        # 获取点击的控件
        child = self.childAt(event.pos())
        # 如果点击的是标题栏或其子控件（除了关闭按钮）
        is_title_area = (child and (child.objectName() == "titleBar" or 
                        (child.parent() and child.parent().objectName() == "titleBar" and
                         child.objectName() != "closeButton")))
        
        if event.button() == Qt.LeftButton and is_title_area:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        event.accept()
        
    def update_loading_animation(self):
        """更新加载动画"""
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        self.result_display.setText(f"正在起卦中{dots}")
            
    def on_divine_clicked(self):
        """处理起卦按钮点击事件"""
        # 如果动画正在播放，忽略新的请求
        if hasattr(self, 'is_animating') and self.is_animating:
            return
            
        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "提示", "请输入您的问题")
            return
            
        # 设置动画状态
        self.is_animating = True
        self.has_result = False  # 添加结果标志
        
        # 禁用输入和按钮
        self.divine_button.setEnabled(False)
        self.question_input.setEnabled(False)
        
        # 开始加载动画
        self.loading_timer.start(500)
        
        # 立即开始播放动画效果
        self.result_display.opacity = 0.0
        self.result_display.scale = 0.5
        self.result_display.setText("正在起卦中...")
        
        # 显示粒子效果
        self.particle_effect.show()
        self.particle_effect.start()
        
        # 等待粒子效果完成后显示太极图（3.5秒）
        QTimer.singleShot(3500, self.show_taiji_animation)
        
        # 创建并启动工作线程
        self.divination_thread = DivinationThread(self.api_client, question)
        self.divination_thread.finished.connect(self.handle_divination_result)
        self.divination_thread.start()
    
    def handle_divination_result(self, result, success):
        """处理占卜结果"""
        # 停止加载动画
        if hasattr(self, 'loading_timer'):
            self.loading_timer.stop()
        
        if not success:
            # 如果失败，等待当前动画完成后再清理
            def cleanup_after_delay():
                self.cleanup_animations()
                self.is_animating = False
                self.divine_button.setEnabled(True)
                self.question_input.setEnabled(True)
                QMessageBox.warning(self, "错误", "获取结果失败，请重试")
            
            # 给予足够的时间让当前动画完成
            QTimer.singleShot(6000, cleanup_after_delay)
            return
        
        # 标记已有结果
        self.has_result = True
        
        # 保存结果文本
        self.result_animation = self.create_result_animation(result)
        
        # 如果太极图已经显示，开始淡出动画
        if hasattr(self, 'taiji_widget') and self.taiji_widget.isVisible():
            self.taiji_widget.fade_out()
            # 等待淡出完成后显示结果
            QTimer.singleShot(800, self.start_result_display)

    def create_result_animation(self, result_text):
        """创建结果显示动画"""
        # 创建动画组
        animation_group = QSequentialAnimationGroup(self)
        
        # 创建并行动画组（同时进行的动画）
        parallel_group = QParallelAnimationGroup()
        
        # 创建缩放动画
        scale_anim = QPropertyAnimation(self.result_display, b"scale")
        scale_anim.setDuration(1000)
        scale_anim.setStartValue(0.5)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.OutBack)
        
        # 创建透明度动画
        opacity_anim = QPropertyAnimation(self.result_display, b"opacity")
        opacity_anim.setDuration(1000)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 添加动画到并行组
        parallel_group.addAnimation(scale_anim)
        parallel_group.addAnimation(opacity_anim)
        
        # 将并行组添加到序列组
        animation_group.addAnimation(parallel_group)
        
        def on_animation_finished():
            # 启用输入和按钮
            self.divine_button.setEnabled(True)
            self.question_input.setEnabled(True)
            self.question_input.clear()
            # 清理资源
            self.cleanup_animations()
            # 重置动画状态
            self.is_animating = False
            
        animation_group.finished.connect(on_animation_finished)
        
        # 设置结果文本
        self.result_display.setText(result_text)
        
        return animation_group

    def show_taiji_animation(self):
        """显示太极动画"""
        # 确保粒子效果已经停止
        if hasattr(self, 'particle_effect'):
            self.particle_effect.stop()
            self.particle_effect.hide()
        
        # 计算太极图位置（居中）
        if hasattr(self, 'taiji_widget'):
            x = (self.width() - self.taiji_widget.width()) // 2
            y = (self.height() - self.taiji_widget.height()) // 2
            self.taiji_widget.move(x, y)
            self.taiji_widget.start_animation()
            
            # 如果已经有结果，直接开始淡出
            if hasattr(self, 'has_result') and self.has_result:
                self.taiji_widget.fade_out()
                QTimer.singleShot(800, self.start_result_display)
    
    def start_result_display(self):
        """开始显示结果文本"""
        if hasattr(self, 'result_animation') and self.result_animation:
            self.result_animation.start()
        else:
            # 如果结果还没有返回，保持显示"正在起卦中..."
            self.result_display.opacity = 1.0
            self.result_display.scale = 1.0
            
    def cleanup_animations(self):
        """清理所有动画资源"""
        # 停止并隐藏粒子效果
        if hasattr(self, 'particle_effect'):
            self.particle_effect.stop()
            self.particle_effect.hide()
            
        # 停止并隐藏太极图
        if hasattr(self, 'taiji_widget'):
            self.taiji_widget.cleanup()
            
        # 清理线程
        if hasattr(self, 'divination_thread') and self.divination_thread:
            self.divination_thread.quit()
            self.divination_thread.wait()
            self.divination_thread.deleteLater()
            self.divination_thread = None
            
        # 清理动画
        if hasattr(self, 'result_animation') and self.result_animation:
            self.result_animation.stop()
            self.result_animation = None
            
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        self.cleanup_animations()
        super().closeEvent(event) 