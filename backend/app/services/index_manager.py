from elasticsearch import Elasticsearch


class IndexManager:
    INDEX_NAME = "documents"

    @staticmethod
    def get_index_mapping() -> dict:
        return {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "document_id": {"type": "keyword"},
                    "file_name": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    },
                    "page_number": {"type": "integer"},
                    "text": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    },
                    "chunk_index": {"type": "integer"},
                    "uploaded_at": {"type": "date"}
                }
            }
        }

    @classmethod
    def create_index(cls, es_client: Elasticsearch) -> bool:
        try:
            if es_client.indices.exists(index=cls.INDEX_NAME):
                print("Индекс уже существует, пропускаем создание")
                return True

            es_client.indices.create(
                index=cls.INDEX_NAME,
                body=cls.get_index_mapping()
            )
            print("Индекс создан")
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False