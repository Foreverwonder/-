import requests
import json
import time
from requests.adapters import HTTPAdapter, Retry

class CozeAPIClient:
    def __init__(self):
        self.api_key = "pat_By3t8bKtq827xOKDg6xbRcPezf7zzQ1bUrpIfb3KwhnOmagtRFSRJprgGlMFJdU3"
        self.bot_id = "7445600453913968691"
        self.base_url = "https://api.coze.cn/v3"
        
        # 配置连接池
        self.session = requests.Session()
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
        
        # 配置连接适配器
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # 添加请求控制
        self.last_request_time = 0
        self.min_request_interval = 0.5
        self.messages_data = None

    def __del__(self):
        """确保在对象销毁时关闭session"""
        if hasattr(self, 'session'):
            self.session.close()

    def _wait_for_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def send_message(self, question):
        """
        发送问题并获取完整响应
        返回: (str, bool) - (响应文本, 是否成功)
        """
        self._wait_for_rate_limit()
        
        data = {
            "bot_id": self.bot_id,
            "user_id": f"user_{int(time.time())}",
            "additional_messages": [
                {
                    "content_type": "text",
                    "content": question,
                    "role": "user",
                    "name": "User",
                    "type": "question"
                }
            ]
        }
        
        try:
            with self.session.post(
                f"{self.base_url}/chat",
                json=data,
                timeout=30
            ) as response:
                response.raise_for_status()
                result = response.json()
            
            if result.get("code") != 0:
                error_msg = result.get("msg", "未知错误")
                return f"API错误: {error_msg}", False
            
            chat_id = result["data"]["id"]
            conversation_id = result["data"]["conversation_id"]
            
            # 等待完成
            max_wait_time = 60
            start_time = time.time()
            
            while True:
                if time.time() - start_time > max_wait_time:
                    return "等待响应超时，请稍后重试", False
                    
                status = self.check_status(conversation_id, chat_id)
                if status["data"]["status"] == "completed":
                    break
                time.sleep(1)
            
            # 获取消息列表
            messages = self.get_messages(conversation_id, chat_id)
            self.messages_data = messages
            
            if messages.get("code") == 0 and "data" in messages:
                # 找到最后一条回答消息
                answer_messages = [
                    msg.get("content", "")
                    for msg in messages["data"]
                    if msg.get("type") == "answer" and msg.get("content_type") == "text"
                ]
                if answer_messages:
                    # 返回最后一条回答
                    return answer_messages[-1], True
                    
            return "未能获取占卜结果", False
            
        except requests.exceptions.Timeout:
            return "请求超时，请检查网络连接后重试", False
        except requests.exceptions.ConnectionError:
            return "网络连接错误，请检查网络设置", False
        except Exception as e:
            return f"发生错误: {str(e)}", False

    def check_status(self, conversation_id, chat_id):
        with self.session.get(
            f"{self.base_url}/chat/retrieve",
            params={
                "conversation_id": conversation_id,
                "chat_id": chat_id
            }
        ) as response:
            response.raise_for_status()
            return response.json()

    def get_messages(self, conversation_id, chat_id):
        with self.session.get(
            f"{self.base_url}/chat/message/list",
            params={
                "conversation_id": conversation_id,
                "chat_id": chat_id
            }
        ) as response:
            response.raise_for_status()
            return response.json()

    def get_divination(self, question):
        """
        完整的占卜流程
        返回: (str, bool) - (占卜结果或错误信息, 是否成功)
        """
        try:
            return self.send_message(question)
        except Exception as e:
            return f"起卦失败: {str(e)}", False 