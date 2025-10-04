import os
from typing import List
import chromadb
import requests
import json
from sentence_transformers import SentenceTransformer, CrossEncoder



class RAGAgent(object):
    def __init__(self, embeding_mode_config, cross_encoder_config, llm_config, db_config):
        self.embeding_mode_config = embeding_mode_config
        self.cross_encoder_config = cross_encoder_config
        self.llm_config =llm_config
        self.db_config = db_config
        # ====================================
        self.embedding_model = SentenceTransformer(self.embeding_mode_config["model"], cache_folder=self.embeding_mode_config["cache_folder"])
        self.cross_encoder_model = CrossEncoder(self.cross_encoder_config["model"])
        self.chromadb_collection = self.create_db(db_config["db_name"], db_config["collection_name"])
        self.llm_url = self.llm_config["url"]
        self.llm_model = self.llm_config["model"]


    def load_file(self, file):
        chunks = self.split_into_chuncks(file)
        embeds = []
        for chunk in chunks:
            embeds.append(self.embed_chunk(chunk)) 
        self.save_embeddings(chunks, embeds)

    def query_answer(self, query, db_query_k=5, rerank_k=3):
        retrieved_chunks = self.retrieve(query, self.db_config["db_name"], self.db_config["collection_name"], db_query_k)
        if rerank_k > db_query_k:
            rerank_k = db_query_k
        reranked_chunks = self.rerank(query, retrieved_chunks, rerank_k)
        
        answer = self.request_answer(self.llm_url, self.llm_model, query, reranked_chunks)
        print(f"\n完整回答:\n{answer}")


    def split_into_chuncks(self, file):
        chunks = []
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = content.split("\n\n")
        
        return chunks

    def embed_chunk(self, chunk):
        embeded = self.embedding_model.encode(chunk, normalize_embeddings=True)
        embedding_list = embeded.tolist()
        return embedding_list

    def create_db(self, db_name, collection_name):
        chromadb_client = chromadb.PersistentClient(path=db_name)
        chromadb_collection = chromadb_client.get_or_create_collection(collection_name)
        return chromadb_collection

    def save_embeddings(self, chunks, embeds):
        for i, (chunk, embedding) in enumerate(zip(chunks, embeds)):
            self.chromadb_collection.add(
                documents=[chunk],
                embeddings = [embedding],
                ids = [str(i)]
            )

    def retrieve(self, query, db_name, collection_name, top_k):
        chromadb_client = chromadb.PersistentClient(path=db_name)
        chromadb_collection = chromadb_client.get_or_create_collection(collection_name)
        query_embedding = self.embed_chunk(query)
        results = chromadb_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        documents = results['documents'][0]
        return documents

    def rerank(self, query, retrieved_chunks, top_k):
        pairs = []
        for chunk in retrieved_chunks:
            pairs.append((query, chunk))
        scores = self.cross_encoder_model.predict(pairs)
        scored_chunks = list(zip(retrieved_chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        documents = [chunk for chunk, score in scored_chunks[:top_k]]

        return documents
        
    def request_answer(self, url: str, model: str, query: str, chunks: List[str]) -> str:
        prompt = f"""你是一位知识助手，请根据用户的问题和下列片段生成准确的回答。

    用户问题: {query}

    相关片段:
    {"\n\n".join(chunks)}

    请基于上述内容作答，不要编造信息。"""

        print(f"{prompt}\n\n---\n")
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        
        # 用于汇总流式输出的变量
        full_response = ""
        
        try:
            response = requests.post(url=url, json=payload, stream=True)
            response.raise_for_status()
            
            print("流式输出:")
            for line in response.iter_lines():
                if line:
                    try:
                        # 解析JSON响应
                        data = json.loads(line.decode('utf-8'))
                        
                        # 检查是否包含响应内容
                        if 'response' in data:
                            chunk_text = data['response']
                            print(chunk_text, end='', flush=True)  # 实时显示
                            full_response += chunk_text  # 累积到汇总变量
                        
                        # 检查是否完成
                        if data.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return ""
        
        print("\n\n---流式输出完成---")
        return full_response





if __name__ == "__main__":
    embeding_mode_config={
        "model":"shibing624/text2vec-base-chinese",
        "cache_folder": r"E:\huggingface_cache"
    }
    cross_encoder_config={
        "model":'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
    }
    llm_config={
        "url": "http://localhost:11434/api/generate",
        "model": "qwen3:latest"  
    }
    db_config={
        "db_name": "rag_test",
        "collection_name": "default"
    }
    rag_agent = RAGAgent(embeding_mode_config, cross_encoder_config, llm_config, db_config)
    # rag_agent.load_file(file = r"E:\code_project\VideoCode\使用Python构建RAG系统\rag\doc.md")
    rag_agent.query_answer(query = "哆啦A梦使用的3个秘密道具分别是什么？")
    

    







