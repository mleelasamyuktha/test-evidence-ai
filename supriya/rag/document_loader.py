# from pathlib import Path


# class DocumentLoader:

#     def __init__(self, documents_path="rag/documents"):
#         self.documents_path = Path(documents_path)

#     def load_documents(self):
#         documents = []

#         for file_path in self.documents_path.glob("*.txt"):
#             content = file_path.read_text(encoding="utf-8")

#             entities = []

#             for line in content.splitlines():
#                 if line.lower().startswith("entity:"):
#                     entities = [
#                         entity.strip().lower()
#                         for entity in line.split(":", 1)[1].split(",")
#                     ]
#                     break

#             documents.append({
#                 "source": file_path.name,
#                 "entities": entities,
#                 "content": content
#             })

#         return documents


from pathlib import Path
from config.entity_catalog import ENTITY_CATALOG


class DocumentLoader:

    def __init__(self, documents_path="rag/documents"):
        self.documents_path = Path(documents_path)

    def load_documents(self):
        documents = []

        for file_path in self.documents_path.glob("*.txt"):
            content = file_path.read_text(encoding="utf-8")

            entities = self._extract_entities(content)

            documents.append({
                "source": file_path.name,
                "entities": entities,
                "content": content
            })

        return documents

    def _extract_entities(self, content):
        entities = []

        content_lower = content.lower()

        for entity in ENTITY_CATALOG:
            if entity.lower() in content_lower:
                entities.append(entity)

        return entities