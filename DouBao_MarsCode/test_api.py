from gui.api_client import CozeAPIClient
import time
import json

def test_api():
    try:
        # 创建API客户端
        client = CozeAPIClient()
        
        # 测试问题
        test_question = "我今天能赚钱吗？"
        
        # 获取结果
        print("\n发送问题:", test_question)
        result, success = client.send_message(test_question)
        
        # 打印原始返回结果
        print("\n原始返回结果:")
        print(result)
        
        if not success:
            print("API调用失败")
            return
            
        # 等待消息处理完成
        print("\n等待消息处理...")
        time.sleep(2)  # 给API一些处理时间
        
        # 获取并打印完整的消息列表
        print("\n完整的API响应:")
        if client.messages_data:
            print(json.dumps(client.messages_data, ensure_ascii=False, indent=2))
            
            # 打印所有回答消息
            print("\n所有回答消息:")
            if 'data' in client.messages_data:
                for i, msg in enumerate(client.messages_data['data']):
                    if msg.get('type') == 'answer' and msg.get('content_type') == 'text':
                        print(f"\n消息 {i}:")
                        print(msg.get('content', ''))
            else:
                print("未找到消息数据")
        else:
            print("未获取到消息数据")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_api() 