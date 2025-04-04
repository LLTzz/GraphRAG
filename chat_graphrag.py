import os
import pkgutil
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


# 加载环境变量
load_dotenv()

class GraphRAGHandler:
    def __init__(self):
        # Neo4j连接配置
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "ltz030928")


        print(f"尝试连接到Neo4j数据库: {self.uri}")
        print(f"使用用户名: {self.user}")
        
        # 初始化Neo4j图数据库连接
        self.graph = Neo4jGraph(
            url=self.uri,
            username=self.user,
            password=self.password,
            # database="system"
        )
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo"
        )
        
        # 创建Cypher QA Chain
        self.cypher_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True
        )

    def query(self, question):
        """
        使用GraphRAG处理问题并获取答案
        """
        try:
            # 使用Cypher QA Chain获取答案
            answer = self.cypher_chain.run(question)
            return answer
        except Exception as e:
            print(f"GraphRAG查询错误: {str(e)}")
            return "抱歉，我在处理您的问题时遇到了困难。请稍后再试。"

    def __del__(self):
        # 关闭Neo4j连接
        if hasattr(self, 'graph'):
            self.graph.close()

# 创建全局实例
try:
    graphrag_handler = GraphRAGHandler()
    print("GraphRAG处理器初始化成功")
except Exception as e:
    print(f"GraphRAG处理器初始化失败: {str(e)}")
    graphrag_handler = None

class ChatBotGraph:
    def __init__(self):
        if graphrag_handler is None:
            raise Exception("GraphRAG处理器未正确初始化")
        self.graphrag = graphrag_handler

    def chat_main(self, sent):
        """使用GraphRAG处理问题"""
        return self.graphrag.query(sent)

if __name__ == '__main__':
    try:
        handler = ChatBotGraph()
        while True:
            question = input("用户: ")
            answer = handler.chat_main(question)
            print("小助手:", answer)
    except Exception as e:
        print(f"程序运行错误: {str(e)}")

