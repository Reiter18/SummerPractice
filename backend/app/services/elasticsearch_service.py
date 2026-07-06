from elasticsearch import Elasticsearch
from typing import List, Dict, Any
from datetime import datetime


class ElasticsearchService:
    def __init__(self, es_client: Elasticsearch, index_name: str = "documents"):
        self.client = es_client
        self.index_name = index_name

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        indexed_count = 0
        for chunk in chunks:
            doc = {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
                "uploaded_at": datetime.now().isoformat()
            }

            try:
                self.client.index(
                    index=self.index_name,
                    id=chunk["chunk_id"],
                    body=doc
                )
                indexed_count += 1
            except Exception as e:
                print(f"Ошибка индексации: {e}")

        self.client.indices.refresh(index=self.index_name)
        return indexed_count

    def search(self, query: str, size: int = 10, from_: int = 0) -> Dict[str, Any]:
        if not query or not query.strip():
            return {"total": 0, "results": []}

        search_body = {
            "query": {
                "multi_match": {
                    "query": query.strip(),
                    "fields": ["text^2", "file_name"],
                    "type": "best_fields",
                    "analyzer": "russian_analyzer",
                    "fuzziness": "AUTO"
                }
            },
            "from": from_,
            "size": size
        }

        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )

            total = response["hits"]["total"]["value"]
            results = []

            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append({
                    "chunk_id": source["chunk_id"],
                    "document_id": source["document_id"],
                    "file_name": source["file_name"],
                    "page": source["page_number"],
                    "text": source["text"],
                    "score": hit["_score"] or 0.0
                })

            return {"total": total, "results": results}

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return {"total": 0, "results": []}

    def delete_document(self, document_id: str) -> bool:
        try:
            self.client.delete_by_query(
                index=self.index_name,
                body={"query": {"term": {"document_id": document_id}}}
            )
            self.client.indices.refresh(index=self.index_name)
            return True
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            return False