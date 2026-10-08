class DocumentChunker:

    def __init__(self, chunk_size=500, overlap=100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_documents(self, documents):
        chunks = []
        print(documents)

        for document in documents:
            content = document["content"]
            source = document["source"]
            entities = document["entities"]

            start = 0

            while start < len(content):
                end = start + self.chunk_size
                chunk_text = content[start:end].strip()

                if chunk_text:
                    chunks.append({
                        "source": source,
                        "entities": entities,
                        "content": chunk_text
                    })

                start += self.chunk_size - self.overlap

        return chunks