from rag.document_loader import DocumentLoader
from rag.chunker import DocumentChunker
from rag.embedder import EmbeddingGenerator
from rag.vector_store import VectorStore


class RAGRetriever:

    def __init__(self, documents_path="rag/documents"):
        self.loader = DocumentLoader(documents_path)
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingGenerator()

        documents = self.loader.load_documents()
        chunks = self.chunker.chunk_documents(documents)

        embeddings = self.embedder.generate_embeddings(chunks)

        self.vector_store = VectorStore(embeddings.shape[1])
        self.vector_store.add(embeddings, chunks)

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return self.vector_store.search(query_embedding, top_k)