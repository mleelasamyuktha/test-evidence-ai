import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension):
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks = []

    def add(self, embeddings, chunks):
        embeddings = np.asarray(embeddings, dtype="float32")

        self.index.add(embeddings)
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k=5):
        query_embedding = np.asarray(query_embedding, dtype="float32")
        query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append({
                "score": float(score),
                "source": self.chunks[index]["source"],
                "entities": self.chunks[index]["entities"],
                "content": self.chunks[index]["content"]})

        return results