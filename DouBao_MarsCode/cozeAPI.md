# CozeAPI 调用流程文档

## 1. API基本信息

### 1.1 认证信息
```python
api_key = ""
bot_id = "7445600453913968691"
base_url = "https://api.coze.cn/v3"
```

### 1.2 请求头设置
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## 2. 请求流程

### 2.1 发送消息
**Endpoint**: `POST /v3/chat`

**请求格式**:
```python
{
    "bot_id": "bot_id",
    "user_id": "user_timestamp",
    "additional_messages": [
        {
            "content_type": "text",
            "content": "用户问题",
            "role": "user",
            "name": "User",
            "type": "question"
        }
    ]
}
```

**响应格式**:
```python
{
    "code": 0,  # 0表示成功
    "data": {
        "id": "chat_id",
        "conversation_id": "conversation_id"
    }
}
```

### 2.2 检查状态
**Endpoint**: `GET /v3/chat/retrieve`

**请求参数**:
- conversation_id
- chat_id

**响应示例**:
```python
{
    "data": {
        "status": "completed"  # 或 "processing"
    }
}
```

### 2.3 获取消息列表
**Endpoint**: `GET /v3/chat/message/list`

**请求参数**:
- conversation_id
- chat_id

## 3. 完整调用流程

1. **初始化会话**
   - 创建带有重试机制的Session
   - 设置默认请求头
   - 配置速率限制（最小请求间隔0.5秒）

2. **发送问题**
   ```python
   # 1. 构造请求数据
   data = {
       "bot_id": bot_id,
       "user_id": f"user_{timestamp}",
       "additional_messages": [{
           "content": question,
           "content_type": "text",
           "role": "user",
           "name": "User",
           "type": "question"
       }]
   }
   
   # 2. 发送POST请求
   response = session.post(f"{base_url}/chat", json=data)
   ```

3. **等待处理完成**
   ```python
   # 轮询检查状态
   while True:
       status = check_status(conversation_id, chat_id)
       if status["data"]["status"] == "completed":
           break
       time.sleep(1)  # 等待1秒后重试
   ```

4. **获取结果**
   ```python
   # 获取消息列表
   messages = get_messages(conversation_id, chat_id)
   
   # 提取最后一条回答
   answer_messages = [
       msg.get("content", "")
       for msg in messages["data"]
       if msg.get("type") == "answer" and msg.get("content_type") == "text"
   ]
   ```

## 4. 错误处理

### 4.1 主要错误类型
- 网络连接错误 (ConnectionError)
- 请求超时 (Timeout)
- API错误 (非0状态码)
- 响应解析错误

### 4.2 重试机制
```python
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=10,
    max_retries=Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
)
```

## 5. 最佳实践

1. **速率限制**
   - 实现请求间隔控制
   - 默认最小间隔0.5秒

2. **资源管理**
   - 使用session管理连接池
   - 确保正确关闭session

3. **超时控制**
   - 设置合理的请求超时时间
   - 实现最大等待时间限制

4. **错误恢复**
   - 实现优雅的错误处理
   - 提供清晰的错误信息

## 6. 示例代码

```python
def get_divination(question):
    try:
        # 等待速率限制
        _wait_for_rate_limit()
        
        # 发送问题
        response = send_message(question)
        
        # 检查响应
        if response.get("code") != 0:
            return f"API错误: {response.get('msg')}", False
            
        # 获取结果
        chat_id = response["data"]["id"]
        conversation_id = response["data"]["conversation_id"]
        
        # 等待完成
        while True:
            status = check_status(conversation_id, chat_id)
            if status["data"]["status"] == "completed":
                break
            time.sleep(1)
        
        # 获取答案
        messages = get_messages(conversation_id, chat_id)
        answer = extract_answer(messages)
        
        return answer, True
        
    except Exception as e:
        return f"起卦失败: {str(e)}", False 
