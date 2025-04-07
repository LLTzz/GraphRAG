import os
import sys
import requests
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
import json

# 设置默认编码为utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 禁用Neo4j警告日志
logging.getLogger("neo4j").setLevel(logging.ERROR)

class GraphRAGHandler:
    def __init__(self):
        # 加载环境变量
        load_dotenv(encoding='utf-8')
        
        # 打印当前工作目录和环境变量文件路径
        print(f"当前工作目录: {os.getcwd()}")
        env_path = os.path.join(os.getcwd(), '.env')
        print(f".env文件路径: {env_path}")
        print(f".env文件是否存在: {os.path.exists(env_path)}")
        
        # 打印.env文件内容
        if os.path.exists(env_path):
            print("=== .env文件内容 ===")
            with open(env_path, 'r', encoding='utf-8') as f:
                print(f.read())
            print("==================")
        
        # Deepseek API参数
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        print(f"API Key: {'已设置' if self.api_key else '未设置'}")
        
        if not self.api_key:
            raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")
        
        # Neo4j连接参数
        self.uri = "bolt://localhost:7687"
        self.user = "neo4j"
        self.password = "ltz030928"
        
        # 尝试连接Neo4j，如果失败则使用离线模式
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.online_mode = True
        except Exception as e:
            print(f"Neo4j连接失败，切换到离线模式: {str(e)}")
            self.online_mode = False
    
    def get_relevant_info(self, question):  # 获取相关信息，从图数据库中查询
        if not self.online_mode:
            return []
            
        try:  # 连接图数据库，并执行查询
            with self.driver.session() as session:
                # 基础查询，根据问题关键词搜索相关节点
                query = """
                MATCH (n)
                WHERE n.name CONTAINS $keyword
                RETURN n.name as name
                LIMIT 5
                """
                
                # 从问题中提取关键词（这里简单处理，实际应用中可以使用更复杂的NLP方法）
                keyword = question.split()[0]  # 使用问题的第一个词作为关键词
                
                result = session.run(query, keyword=keyword)
                return [record for record in result]
        except Exception as e:
            print(f"查询图数据库时出错: {str(e)}")
            return []
    
    def get_answer_stream(self, question):
        try:
            # 从图数据库获取相关信息
            relevant_info = self.get_relevant_info(question)
            
            # 格式化上下文信息
            context = "\n".join([f"{info['name']}" for info in relevant_info])
            
            # 构建提示
            prompt = f"""你是一个专业的医疗助手。使用以下信息来回答问题。
如果无法从提供的信息中找到答案，请说明你不知道。

上下文信息:
{context}

问题: {question}

请提供准确、专业的回答，并尽可能引用相关的医疗知识。
回答:"""
            
            # 调用Deepseek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的医疗助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "stream": True
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]  # 去掉 'data: ' 前缀
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    content = chunk['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                yield f"API调用失败: {response.text}"
                
        except Exception as e:
            print(f"生成回答时出错: {str(e)}")
            yield f"抱歉，处理您的问题时出现错误: {str(e)}"
    
    def get_answer(self, question):
        return ''.join(self.get_answer_stream(question))
    
    def __del__(self):
        # 关闭数据库连接
        if hasattr(self, 'driver') and self.online_mode:
            self.driver.close()

def main():
    try:
        handler = GraphRAGHandler()
        print("\n=== 医疗知识问答系统 ===")
        print("输入 'quit' 或 'exit' 退出程序")
        
        while True:
            question = input("\n请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit']:
                print("感谢使用，再见！")
                break
                
            if not question:
                print("问题不能为空，请重新输入")
                continue
                
            print("\n正在思考...")
            for chunk in handler.get_answer_stream(question):
                print(chunk, end='', flush=True)
            print("\n")
            
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main() 