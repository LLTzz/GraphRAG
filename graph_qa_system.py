from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from chat_deepseek_api import GraphRAGHandler
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 初始化问答处理器
try:
    handler = GraphRAGHandler()
    if handler.online_mode:
        logger.info("成功初始化问答处理器（在线模式）")
    else:
        logger.info("成功初始化问答处理器（离线模式）")
except Exception as e:
    logger.error(f"初始化问答处理器失败: {str(e)}")
    handler = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    if handler is None:
        return jsonify({
            'status': 'error',
            'message': '系统未正确初始化'
        }), 500
    
    return jsonify({
        'status': 'ok',
        'message': '系统正常运行',
        'mode': 'online' if handler.online_mode else 'offline'
    })

@app.route('/ask', methods=['POST'])
def ask():
    if handler is None:
        return jsonify({
            'error': '系统未正确初始化'
        }), 500
        
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
            
        def generate():
            try:
                for chunk in handler.get_answer_stream(question):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            except Exception as e:
                logger.error(f"生成回答时出错: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                yield "data: [DONE]\n\n"
                
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"处理问题时出错: {str(e)}")
        return jsonify({
            'error': '处理您的问题时出现错误',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 