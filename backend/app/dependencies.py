from elasticsearch import Elasticsearch
from app.config import settings


def get_elasticsearch_client() -> Elasticsearch:
    client = Elasticsearch(
        settings.elasticsearch_url,
        request_timeout=30,
        retry_on_timeout=True,
        max_retries=3
    )
    try:
        client.info()
        return client
    except Exception as e:
        print(f"Не удалось подключиться к Elasticsearch: {e}")
        return client