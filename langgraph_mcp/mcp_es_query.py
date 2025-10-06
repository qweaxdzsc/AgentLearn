from mcp.server.fastmcp import FastMCP
from elasticsearch import Elasticsearch
import json
from datetime import datetime
from typing import Dict, List, Any

from elasticsearch_demo import ElasticsearchDemo

mcp = FastMCP("es_query", port=5005)


@mcp.tool()
def search_and_display(query_text: str, max_results: int = 10) -> str:
    """
    搜索并显示结果（类似 main 函数的功能）
    
    Args:
        query_text: 搜索查询文本
        max_results: 最大返回结果数量
    """
    try:
        # 初始化客户端
        es_demo = ElasticsearchDemo()
        
        # 检查连接
        if not es_demo.check_connection():
            return "Elasticsearch 连接失败，请确保服务正在运行"
        
        # 确保索引存在
        es_demo.create_index()
        
        # 构建搜索查询
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title", "content", "tags"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        }
        
        # 执行搜索
        results = es_demo.search_documents(query, size=max_results)
        
        if not results:
            return "未找到相关文档"
        
        # 构建结果字符串
        result_lines = []
        result_lines.append(f"找到 {len(results)} 个相关文档:")
        result_lines.append("-" * 30)
        
        for i, doc in enumerate(results, 1):
            result_lines.append(f"{i}. 标题: {doc['title']}")
            result_lines.append(f"   作者: {doc['author']}")
            result_lines.append(f"   内容: {doc['content'][:100]}...")
            result_lines.append(f"   标签: {doc['tags']}")
            result_lines.append(f"   浏览量: {doc['views']}")
            result_lines.append(f"   相关度分数: {doc.get('_score', 'N/A')}")
            result_lines.append("-" * 30)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"搜索出错: {str(e)}"
    




if __name__ == "__main__":
    # 以sse协议暴露服务。 
    mcp.settings.host = "0.0.0.0"
    mcp.run(transport='streamable-http') 
    # 以stdio协议暴露服务。
    # mcp.run(transport='stdio')
 
 