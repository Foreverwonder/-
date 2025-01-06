from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QPropertyAnimation, QPointF, QRectF, QTimer, pyqtProperty, QObject, QEasingCurve
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush

class TaijiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        
        # 初始化场景和视图
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setFrameShape(QGraphicsView.NoFrame)
        
        # 调整视图大小和位置
        self.view.setFixedSize(self.size())
        self.view.setSceneRect(-100, -100, 200, 200)
        self.view.setAlignment(Qt.AlignCenter)
        
        # 创建太极图形
        self.taiji = TaijiItem()
        self.scene.addItem(self.taiji)
        
        # 设置动画
        self.rotation_anim = QPropertyAnimation(self.taiji.animation_proxy, b"rotation")
        self.opacity_anim = QPropertyAnimation(self.taiji.animation_proxy, b"opacity")
        
        # 初始化隐藏
        self.hide()
        self.is_animating = False
        
    def resizeEvent(self, event):
        """处理大小改变事件"""
        super().resizeEvent(event)
        self.view.setFixedSize(self.size())
        self.view.setSceneRect(-self.width()/2, -self.height()/2, self.width(), self.height())
        
    def reset_state(self):
        """重置所有状态"""
        self.rotation_anim.stop()
        self.opacity_anim.stop()
        self.taiji.setRotation(0)
        self.taiji.setOpacity(0)
        self.is_animating = False
        self.hide()
        
    def start_animation(self):
        """开始旋转和渐显动画"""
        if self.is_animating:
            return
            
        self.is_animating = True
        self.reset_state()
        self.show()
        
        # 配置旋转动画
        self.rotation_anim.setDuration(3000)  # 3秒转一圈
        self.rotation_anim.setStartValue(0)
        self.rotation_anim.setEndValue(360)
        self.rotation_anim.setEasingCurve(QEasingCurve.Linear)  # 使用线性动画使旋转更均匀
        self.rotation_anim.setLoopCount(-1)  # 设置无限循环
        
        # 配置透明度动画（渐显）
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 启动动画
        self.rotation_anim.start()
        self.opacity_anim.start()
        
    def fade_out(self):
        """开始渐隐动画"""
        if not self.is_animating:
            return
            
        # 停止旋转动画
        self.rotation_anim.stop()
        
        # 配置并启动淡出动画
        self.opacity_anim.stop()
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setStartValue(1)
        self.opacity_anim.setEndValue(0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_anim.finished.connect(self.cleanup)  # 淡出完成后清理
        self.opacity_anim.start()
        
    def cleanup(self):
        """清理资源"""
        self.reset_state()

class TaijiAnimationProxy(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._rotation = 0.0
        self._item = None

    def setItem(self, item):
        self._item = item

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        if self._opacity != value:
            self._opacity = value
            if self._item:
                self._item.setOpacity(value)

    @pyqtProperty(float)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if self._rotation != value:
            self._rotation = value
            if self._item:
                self._item.setRotation(value)

class TaijiItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self._opacity = 1.0
        self.animation_proxy = TaijiAnimationProxy()
        self.animation_proxy.setItem(self)
        self.setAcceptHoverEvents(False)
        
    def type(self):
        """返回图形项类型"""
        return QGraphicsItem.UserType + 1
        
    def boundingRect(self):
        return QRectF(-100, -100, 200, 200)

    def setOpacity(self, value):
        if self._opacity != value:
            self._opacity = value
            self.update()

    def setRotation(self, value):
        super().setRotation(value)
        self.update()
            
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置透明度
        painter.setOpacity(self._opacity)

        # 绘制外圆
        painter.setPen(Qt.NoPen)  # 避免边框干扰
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(self.boundingRect())

        # 绘制白色部分（直接覆盖黑色外圆的一部分）
        path_white = QPainterPath()
        path_white.moveTo(0, 0)
        path_white.arcTo(-100, -100, 200, 200, 90, 180)  # 外圆弧
        path_white.arcTo(-50, -100, 100, 100, 270, 180)  # 上半内圆
        path_white.arcTo(-50, 0, 100, 100, 90, 180)      # 下半内圆
        path_white.closeSubpath()
        painter.setBrush(QBrush(Qt.white))
        painter.drawPath(path_white)

        # 绘制黑色部分（完全覆盖白色的一部分）
        path_black = QPainterPath()
        path_black.moveTo(0, 0)
        path_black.arcTo(-100, -100, 200, 200, 270, 180)  # 外圆弧
        path_black.arcTo(-50, 0, 100, 100, 90, 180)       # 下半内圆
        path_black.arcTo(-50, -100, 100, 100, 270, 180)   # 上半内圆
        path_black.closeSubpath()
        painter.setBrush(QBrush(Qt.black))
        painter.drawPath(path_black)

        # 绘制小圆
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(QRectF(-25, -75, 50, 50))  # 白色半圆中的小黑圆

        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(QRectF(-25, 25, 50, 50))  # 黑色半圆中的小白圆