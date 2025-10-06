#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticsearch 极简交互示例
包括数据写入和查询功能
"""

from elasticsearch import Elasticsearch
import json
from datetime import datetime
from typing import Dict, List, Any


class ElasticsearchDemo:
    def __init__(self, host: str = "localhost", port: int = 9200):
        """
        初始化 Elasticsearch 客户端
        
        Args:
            host: Elasticsearch 服务器地址
            port: Elasticsearch 服务器端口
        """
        # Elasticsearch 9.x 版本需要不同的配置
        self.es = Elasticsearch(
            [f"http://{host}:{port}"],
            verify_certs=False,
            ssl_show_warn=False,
            request_timeout=30
        )
        self.index_name = "demo_index"
        
    def check_connection(self) -> bool:
        """检查 Elasticsearch 连接状态"""
        try:
            if self.es.ping():
                print("Elasticsearch 连接成功")
                return True
            else:
                print("Elasticsearch 连接失败")
                return False
        except Exception as e:
            print(f"连接错误: {e}")
            return False
    
    def create_index(self) -> bool:
        """创建索引"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # 定义索引映射
                mapping = {
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "author": {"type": "keyword"},
                            "tags": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "views": {"type": "integer"},
                            "is_published": {"type": "boolean"}
                        }
                    }
                }
                self.es.indices.create(index=self.index_name, **mapping)
                print(f"索引 '{self.index_name}' 创建成功")
            else:
                print(f"索引 '{self.index_name}' 已存在")
            return True
        except Exception as e:
            print(f"创建索引失败: {e}")
            return False
    
    def insert_document(self, doc: Dict[str, Any], doc_id: str = None) -> bool:
        """
        插入单个文档
        
        Args:
            doc: 要插入的文档数据
            doc_id: 文档ID，如果不提供则自动生成
            
        Returns:
            bool: 插入是否成功
        """
        try:
            # 添加时间戳
            doc["created_at"] = datetime.now().isoformat()
            
            if doc_id:
                result = self.es.index(index=self.index_name, id=doc_id, document=doc)
            else:
                result = self.es.index(index=self.index_name, document=doc)
            
            print(f"文档插入成功，ID: {result['_id']}")
            return True
        except Exception as e:
            print(f"插入文档失败: {e}")
            return False
    
    def bulk_insert(self, docs: List[Dict[str, Any]]) -> bool:
        """
        批量插入文档
        
        Args:
            docs: 要插入的文档列表
            
        Returns:
            bool: 批量插入是否成功
        """
        try:
            actions = []
            for i, doc in enumerate(docs):
                # 添加时间戳
                doc["created_at"] = datetime.now().isoformat()
                
                action = {
                    "index": {
                        "_index": self.index_name,
                        "_source": doc
                    }
                }
                actions.append(action)
            
            # 执行批量插入
            result = self.es.bulk(operations=actions)
            
            if result["errors"]:
                print("批量插入部分失败")
                for item in result["items"]:
                    if "error" in item["index"]:
                        print(f"错误: {item['index']['error']}")
            else:
                print(f"批量插入成功，共 {len(docs)} 个文档")
            
            return True
        except Exception as e:
            print(f"批量插入失败: {e}")
            return False
    
    def search_documents(self, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """
        搜索文档
        
        Args:
            query: 搜索查询
            size: 返回结果数量
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            result = self.es.search(
                index=self.index_name,
                query=query["query"],
                size=size
            )
            
            hits = result["hits"]["hits"]
            print(f"找到 {result['hits']['total']['value']} 个结果")
            
            documents = []
            for hit in hits:
                doc = hit["_source"]
                doc["_id"] = hit["_id"]
                doc["_score"] = hit["_score"]
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        根据ID获取文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            Dict: 文档数据
        """
        try:
            result = self.es.get(index=self.index_name, id=doc_id)
            doc = result["_source"]
            doc["_id"] = result["_id"]
            return doc
        except Exception as e:
            print(f"获取文档失败: {e}")
            return {}
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            result = self.es.delete(index=self.index_name, id=doc_id)
            print(f"文档 {doc_id} 删除成功")
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        try:
            stats = self.es.indices.stats(index=self.index_name)
            return stats["indices"][self.index_name]
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}


def main():
    """主函数 - 演示 Elasticsearch 基本操作"""
    print("Elasticsearch 极简交互示例")
    print("=" * 50)
    
    # 初始化客户端
    es_demo = ElasticsearchDemo()
    
    # 检查连接
    if not es_demo.check_connection():
        print("请确保 Elasticsearch 服务正在运行")
        return
    
    # 创建索引
    es_demo.create_index()
    
    # 示例数据
    sample_docs = [
        {
            "title": "Python 编程入门",
            "content": "Python 是一种简单易学的编程语言，适合初学者学习。",
            "author": "张三",
            "tags": ["Python", "编程", "入门"],
            "views": 100,
            "is_published": True
        },
        {
            "title": "Elasticsearch 基础教程",
            "content": "Elasticsearch 是一个分布式搜索和分析引擎。",
            "author": "李四",
            "tags": ["Elasticsearch", "搜索", "数据库"],
            "views": 150,
            "is_published": True
        },
        {
            "title": "机器学习实战",
            "content": "机器学习是人工智能的一个重要分支。",
            "author": "王五",
            "tags": ["机器学习", "AI", "算法"],
            "views": 200,
            "is_published": False
        }
    ]
    
    print("\n插入示例数据")
    print("-" * 30)
    
    # 插入单个文档
    es_demo.insert_document(sample_docs[0], "doc_1")
    
    # 批量插入文档
    es_demo.bulk_insert(sample_docs[1:])
    
    print("\n搜索示例")
    print("-" * 30)
    
    # 1. 全文搜索
    print("1. 全文搜索 'Python':")
    query = {
        "query": {
            "match": {
                "content": "Python"
            }
        }
    }
    results = es_demo.search_documents(query)
    for doc in results:
        print(f"  - {doc['title']} (作者: {doc['author']})")
    
    # 2. 精确匹配
    print("\n2. 精确匹配作者 '张三':")
    query = {
        "query": {
            "term": {
                "author": "张三"
            }
        }
    }
    results = es_demo.search_documents(query)
    for doc in results:
        print(f"  - {doc['title']}")
    
    # 3. 范围查询
    print("\n3. 浏览量大于 120 的文章:")
    query = {
        "query": {
            "range": {
                "views": {
                    "gte": 120
                }
            }
        }
    }
    results = es_demo.search_documents(query)
    for doc in results:
        print(f"  - {doc['title']} (浏览量: {doc['views']})")
    
    # 4. 布尔查询
    print("\n4. 已发布且包含 '搜索' 标签的文章:")
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"is_published": True}},
                    {"term": {"tags": "搜索"}}
                ]
            }
        }
    }
    results = es_demo.search_documents(query)
    for doc in results:
        print(f"  - {doc['title']} (标签: {doc['tags']})")
    
    print("\n获取文档详情")
    print("-" * 30)
    
    # 根据ID获取文档
    doc = es_demo.get_document_by_id("doc_1")
    if doc:
        print(f"文档详情: {json.dumps(doc, ensure_ascii=False, indent=2)}")
    
    print("\n索引统计信息")
    print("-" * 30)
    
    stats = es_demo.get_index_stats()
    if stats:
        print(f"文档总数: {stats['total']['docs']['count']}")
        print(f"索引大小: {stats['total']['store']['size_in_bytes']} 字节")
    
    print("\n演示完成!")


if __name__ == "__main__":
    main()
