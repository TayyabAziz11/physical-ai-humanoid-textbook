# backend/app/services/rag.py

from qdrant_client import QdrantClient

class RagRetriever:
    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int = 5):
        # Basic example using Qdrant search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=self.embed_text(query),
            limit=top_k
        )
        # Return just payloads/text
        return [hit.payload["text"] for hit in search_result]

    def embed_text(self, text: str):
        # Use OpenAI embeddings or a dummy vector for now
        from openai import OpenAI
        client = OpenAI()
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return embedding.data[0].embedding

class RagChat:
    def __init__(self, retriever: RagRetriever):
        self.retriever = retriever

    def answer(self, query: str) -> str:
        chunks = self.retriever.retrieve(query)
        if not chunks:
            return "No relevant information found."
        # For simplicity, just concatenate top chunks
        return "\n\n".join(chunks)
