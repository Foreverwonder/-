# 易学决策分析应用

## 产品定位
- 面向年轻用户群的现代化易学决策分析应用
- 结合传统文化与现代设计美学
- 简单易用，富有神秘感

## 核心功能
1. 用户输入咨询问题
2. 通过Coze API进行易学起卦
3. 展示卦象结果与解释

## UI设计方案

### 主题设计
- 整体色调：深紫色(#2C1810)搭配金色(#D4AF37)点缀
- 设计风格：新中式玄学风格，融合现代极简主义
- 特效：关键位置添加粒子动效，提升神秘感

### 界面布局
1. 顶部区域
   - 应用名称/Logo
   - 简约的装饰纹样

2. 中央区域
   - 太极卦象动态展示区
   - 圆形或八卦形状的起卦按钮
   - 优雅的输入框设计
   - 动态太极八卦图
     * 粒子效果结束后优雅呈现
     * 平滑旋转动画（约3-5秒）
     * 渐隐过渡效果
     * 传统太极配色（黑白阴阳）搭配金色描边

3. 底部区域
   - 卦象结果详细解释
   - 动态过渡效果

## 交互流程
1. 启动应用 → 展示优雅的加载动画
2. 主界面呈现 → 引导用户输入问题
3. 点击起卦 → 显示动态卦象生成效果
4. 展示结果 → 优雅展现卦象与解释

## 技术实现要点
1. 使用Python + PyQt6开发GUI界面
2. 接入Coze API进行卦象生成
3. 使用QSS实现现代化UI样式
4. 添加粒子效果和过渡动画

## 开发计划
1. Phase 1: UI框架搭建
2. Phase 2: API对接
3. Phase 3: 动效开发
4. Phase 4: 测试优化

## 后续优化方向
1. 添加卦象历史记录
2. 支持分享功能
3. 加入更多动态效果
4. 优化交互体验 

扣子API_key：pat_By3t8bKtq827xOKDg6xbRcPezf7zzQ1bUrpIfb3KwhnOmagtRFSRJprgGlMFJdU3
易学决策分析botid：
7445600453913968691
官方文档链接https://www.coze.cn/docs/developer_guides/coze_api_overview
### 3. 请求/响应流程
1. **发送问题请求**
   ```json
   {
       "botId": "BOT_ID",
       "messages": [
           {
               "role": "user",
               "content": "用户问题"
           }
       ],
       "stream": false
   }
   ```

2. **接收初始响应**
   ```json
   {
       "id": "completion_id",
       "object": "chat.completion",
       "created": 1699495740,
       "choices": [
           {
               "index": 0,
               "message": {
                   "role": "assistant",
                   "content": "卦象解析结果"
               },
               "finish_reason": "stop"
           }
       ]
   }
   ```

### 4. 优化建议的 API 客户端结构
```python
class CozeAPIClient:
    def __init__(self):
        self.api_key = "YOUR_API_KEY"
        self.bot_id = "BOT_ID"
        self.base_url = "https://www.coze.cn/api/v1"

    def send_question(self, question):
        """发送问题并获取初始响应"""
        # 实现发送逻辑
        pass

    def get_completion_result(self, completion_id):
        """获取特定 completion_id 的结果"""
        # 实现查询逻辑
        pass

    def get_divination(self, question):
        """完整的占卜流程"""
        # 1. 发送问题
        # 2. 获取 completion_id
        # 3. 查询结果
        # 4. 返回最终解析
        pass
```

### 4. 错误处理机制

1. **HTTP 错误处理**
   - 超时设置：30秒
   - 重试机制：最多3次
   - 网络错误处理
   - SSL验证

2. **API 错误码处理**
   - code = 0: 成功
   - code = 700012006: 认证失败
   - 其他错误码: 根据 msg 字段显示具体错误

3. **重试策略**
```python
retry_strategy = requests.adapters.Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
```