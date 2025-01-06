from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QPointF, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (QPainter, QColor, QRadialGradient, QPainterPath, QPen,
                        QTransform)
import random
import math

class ParticleEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        
        if parent:
            self.setParent(parent)
            self.move(0, 0)
        
        self.particles = []
        self.is_active = False
        self.fade_out = False
        self.effect_duration = 3500  # 延长到3.5秒
        self.max_particles = 100  # 减少粒子数量，让效果不那么密集
        
        # 太极动画相关
        self._taiji_opacity = 0.0
        self._taiji_scale = 0.1
        self.taiji_rotation = 0.0
        self.showing_taiji = False
        
        # 定义传统色彩
        self.colors = [
            (212, 175, 55),  # 金色
            (255, 215, 0),   # 明金色
            (218, 165, 32),  # 暗金色
            (184, 134, 11)   # 深金色
        ]
        
        # 八卦符号路径缓存
        self.bagua_paths = self.create_bagua_paths()
        self.taiji_path = self.create_taiji_path()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        
        self.effect_timer = QTimer(self)
        self.effect_timer.timeout.connect(self.start_taiji_animation)
        self.effect_timer.setSingleShot(True)
        
        # 动画对象
        self.fade_in_animation = None
        self.scale_animation = None
        self.fade_out_animation = None
        self.rotation_timer = None
    
    def create_bagua_paths(self):
        """创建八卦符号的路径"""
        paths = []
        
        # 创建阴阳爻的基本路径
        yin_path = QPainterPath()
        yin_path.moveTo(-10, 0)
        yin_path.lineTo(-5, 0)
        yin_path.moveTo(5, 0)
        yin_path.lineTo(10, 0)
        
        yang_path = QPainterPath()
        yang_path.moveTo(-10, 0)
        yang_path.lineTo(10, 0)
        
        # 创建阴阳鱼路径
        taiji_path = QPainterPath()
        taiji_path.arcTo(-10, -10, 20, 20, 90, 180)
        taiji_path.arcTo(-5, -10, 10, 10, 270, 180)
        taiji_path.arcTo(-5, 0, 10, 10, 90, 180)
        taiji_path.arcTo(-10, -10, 20, 20, 270, 180)
        
        paths.extend([yin_path, yang_path, taiji_path])
        return paths
    
    def create_taiji_path(self):
        """创建完整的太极图案的两个部分"""
        # 白色部分的路径（整个圆）
        white_path = QPainterPath()
        white_path.addEllipse(-50, -50, 100, 100)
        
        # 黑色部分的路径（优化阴阳鱼形状）
        black_path = QPainterPath()
        
        # 使用贝塞尔曲线创建更平滑的S形
        black_path.moveTo(0, -50)  # 从顶部中心开始
        
        # 左半圆
        black_path.arcTo(-50, -50, 100, 100, 90, 180)
        
        # 使用三次贝塞尔曲线创建S形过渡
        black_path.cubicTo(
            -25, 0,   # 第一个控制点
            25, 0,    # 第二个控制点
            0, 50     # 终点
        )
        
        # 右半圆
        black_path.arcTo(-50, -50, 100, 100, 270, -180)
        
        # 使用三次贝塞尔曲线完成S形
        black_path.cubicTo(
            25, 0,    # 第一个控制点
            -25, 0,   # 第二个控制点
            0, -50    # 终点（回到起点）
        )
        
        # 确保路径闭合
        black_path.closeSubpath()
        
        # 添加内部的小圆
        inner_radius = 12.5
        black_path.addEllipse(-inner_radius, -25, inner_radius*2, inner_radius*2)  # 上半部分小圆
        white_path.addEllipse(-inner_radius, 25-inner_radius*2, inner_radius*2, inner_radius*2)  # 下半部分小圆
        
        return (white_path, black_path)
    
    def start_taiji_animation(self):
        """开始太极图动画"""
        # 确保清理之前的动画
        self.cleanup()
        
        self.showing_taiji = True
        self._taiji_opacity = 0.0
        self._taiji_scale = 0.1
        self.taiji_rotation = 0.0
        
        try:
            # 创建并启动淡入动画
            self.fade_in_animation = QPropertyAnimation(self, b'taiji_opacity')
            self.fade_in_animation.setStartValue(0.0)
            self.fade_in_animation.setEndValue(1.0)
            self.fade_in_animation.setDuration(1000)
            self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # 创建并启动缩放动画
            self.scale_animation = QPropertyAnimation(self, b'taiji_scale')
            self.scale_animation.setStartValue(0.1)
            self.scale_animation.setEndValue(1.0)
            self.scale_animation.setDuration(1000)
            self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
            
            # 启动动画
            self.fade_in_animation.start()
            self.scale_animation.start()
            
            # 设置旋转计时器
            self.rotation_timer = QTimer(self)
            self.rotation_timer.timeout.connect(self.update_rotation)
            self.rotation_timer.start(16)  # 约60FPS
            
            # 设置消失计时器
            QTimer.singleShot(3000, self.start_fade_out)
            
        except Exception as e:
            print(f"启动太极动画时出错: {e}")
            self.cleanup()  # 出错时清理资源
    
    def start_fade_out(self):
        """开始淡出动画"""
        self.fade_out_animation = QPropertyAnimation(self, b'taiji_opacity')
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setDuration(1000)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self.cleanup)
        self.fade_out_animation.start()
    
    def cleanup(self):
        """清理动画相关资源"""
        try:
            # 停止所有计时器和动画
            if self.rotation_timer:
                self.rotation_timer.stop()
                self.rotation_timer.deleteLater()
                self.rotation_timer = None
                
            if self.fade_in_animation:
                self.fade_in_animation.stop()
                self.fade_in_animation.deleteLater()
                self.fade_in_animation = None
                
            if self.scale_animation:
                self.scale_animation.stop()
                self.scale_animation.deleteLater()
                self.scale_animation = None
                
            if self.fade_out_animation:
                self.fade_out_animation.stop()
                self.fade_out_animation.deleteLater()
                self.fade_out_animation = None
            
            # 重置所有状态
            self.showing_taiji = False
            self._taiji_opacity = 0.0
            self._taiji_scale = 0.1
            self.taiji_rotation = 0.0
            
            # 强制更新显示
            self.update()
            
        except Exception as e:
            print(f"清理动画资源时出错: {e}")
        finally:
            self.hide()
    
    def update_rotation(self):
        """更新太极图旋转角度"""
        self.taiji_rotation += 2  # 每帧旋转2度
        if self.taiji_rotation >= 360:
            self.taiji_rotation = 0
        self.update()
    
    # Qt属性定义
    @property
    def taiji_opacity(self):
        return self._taiji_opacity
    
    @taiji_opacity.setter
    def taiji_opacity(self, value):
        self._taiji_opacity = value
        self.update()
    
    @property
    def taiji_scale(self):
        return self._taiji_scale
    
    @taiji_scale.setter
    def taiji_scale(self, value):
        self._taiji_scale = value
        self.update()
    
    def start(self):
        """开始粒子效果"""
        self.particles.clear()
        self.is_active = True
        self.fade_out = False
        if self.parent():
            self.resize(self.parent().size())
            self.move(0, 0)
        self.timer.start(16)  # 约60FPS
        self.effect_timer.start(self.effect_duration)
        self.show()
        self.raise_()
        
    def stop(self):
        """停止粒子效果"""
        self.fade_out = True
        self.effect_timer.stop()
        if not self.particles:
            self.is_active = False
            self.timer.stop()
            self.hide()
    
    def add_particles(self, count):
        """添加多个粒子"""
        if not self.parent():
            return
            
        center_x = self.width() / 2
        center_y = self.height() * 0.8  # 更靠下的起始位置
        
        for _ in range(count):
            # 创建方形起源区域
            x = center_x + random.uniform(-30, 30)  # 缩小起源区域
            y = center_y + random.uniform(-5, 5)    # 缩小起源区域
            
            # 螺旋式上升路径
            base_angle = random.uniform(0, math.pi * 2)
            spiral_radius = random.uniform(30, 120)  # 增加螺旋半径范围
            upward_speed = random.uniform(1.5, 2.5)  # 降低上升速度
            
            # 随机选择颜色
            base_color = random.choice(self.colors)
            
            # 随机选择符号类型
            symbol_type = random.randint(0, len(self.bagua_paths) - 1)
            
            particle = {
                'pos': QPointF(x, y),
                'base_angle': base_angle,
                'spiral_radius': spiral_radius,
                'upward_speed': upward_speed,
                'life': random.randint(100, 180),  # 延长粒子生命周期
                'max_life': 180,  # 延长最大生命周期
                'size': random.uniform(10, 18),  # 略微增大粒子尺寸
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-1, 1),  # 降低旋转速度
                'symbol_type': symbol_type,
                'color': QColor(*base_color),
                'phase': 0.0
            }
            self.particles.append(particle)
    
    def update_particles(self):
        if not self.is_active:
            return
            
        for particle in self.particles:
            # 更新螺旋运动
            particle['base_angle'] += 0.03  # 降低螺旋速度
            radius = particle['spiral_radius'] * (1 - particle['life'] / particle['max_life'])
            
            x = particle['pos'].x() + math.cos(particle['base_angle']) * radius
            y = particle['pos'].y() - particle['upward_speed']
            particle['pos'] = QPointF(x, y)
            
            # 更新旋转
            particle['rotation'] += particle['rotation_speed']
            
            # 更新颜色相位
            particle['phase'] += 0.01  # 降低颜色变化速度
            if particle['phase'] >= 1.0:
                particle['phase'] = 0.0
                next_color = random.choice(self.colors)
                particle['color'] = QColor(*next_color)
            
            # 更新生命周期
            particle['life'] -= 1
        
        # 移除消失的粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # 添加新粒子，减少每次添加的数量
        if not self.fade_out and len(self.particles) < self.max_particles:
            self.add_particles(3)  # 每次只添加3个粒子
            
        if self.fade_out and not self.particles:
            self.is_active = False
            self.timer.stop()
            self.hide()
            
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.is_active:
            self.paint_particles(painter)
        
        if self.showing_taiji:
            self.paint_taiji(painter)
    
    def paint_taiji(self, painter):
        """绘制太极图"""
        if not self.showing_taiji:
            return
            
        painter.save()
        
        try:
            # 移动到中心点
            painter.translate(self.width() / 2, self.height() / 2)
            
            # 应用旋转和缩放
            painter.rotate(self.taiji_rotation)
            painter.scale(self.taiji_scale, self.taiji_scale)
            
            # 设置透明度
            painter.setOpacity(self.taiji_opacity)
            
            # 使用最高质量渲染
            painter.setRenderHints(
                QPainter.Antialiasing |
                QPainter.SmoothPixmapTransform |
                QPainter.HighQualityAntialiasing
            )
            
            # 获取路径
            white_path, black_path = self.taiji_path
            
            # 绘制白色背景
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPath(white_path)
            
            # 绘制黑色部分
            painter.setBrush(QColor(0, 0, 0))
            painter.drawPath(black_path)
            
            # 计算小圆点尺寸和位置
            dot_radius = 8  # 小圆点半径
            bg_radius = 10  # 背景圆半径
            dot_offset = 33  # 偏移量
            
            # 绘制小圆点时使用完整的圆形路径
            # 上部分的小圆（黑色）
            white_dot_bg = QPainterPath()
            white_dot_bg.addEllipse(QPointF(0, -dot_offset), bg_radius, bg_radius)
            black_dot = QPainterPath()
            black_dot.addEllipse(QPointF(0, -dot_offset), dot_radius, dot_radius)
            
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPath(white_dot_bg)
            painter.setBrush(QColor(0, 0, 0))
            painter.drawPath(black_dot)
            
            # 下部分的小圆（白色）
            black_dot_bg = QPainterPath()
            black_dot_bg.addEllipse(QPointF(0, dot_offset), bg_radius, bg_radius)
            white_dot = QPainterPath()
            white_dot.addEllipse(QPointF(0, dot_offset), dot_radius, dot_radius)
            
            painter.setBrush(QColor(0, 0, 0))
            painter.drawPath(black_dot_bg)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPath(white_dot)
            
        finally:
            painter.restore()
    
    def paint_particles(self, painter):
        """绘制粒子效果"""
        for particle in self.particles:
            opacity = particle['life'] / particle['max_life']
            painter.save()
            
            color = particle['color']
            painter.setOpacity(opacity)
            
            painter.translate(particle['pos'])
            painter.rotate(particle['rotation'])
            
            scale = particle['size'] / 20.0
            painter.scale(scale, scale)
            
            path = self.bagua_paths[particle['symbol_type']]
            
            glow = QRadialGradient(QPointF(0, 0), particle['size'] * 2)
            glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), int(255 * opacity)))
            glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            
            painter.setBrush(glow)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(0, 0), particle['size'], particle['size'])
            
            pen = QPen(color, 2)
            painter.setPen(pen)
            painter.drawPath(path)
            
            painter.restore()
