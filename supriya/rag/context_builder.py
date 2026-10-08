class RAGContextBuilder:

    def build_context(self, results):
        if not results:
            return "No relevant historical business knowledge was retrieved."

        context_parts = []

        for i, result in enumerate(results, start=1):
            entities = ", ".join(result.get("entities", []))

            context_parts.append(
                f"""Historical Knowledge {i}
Source: {result["source"]}
Entities: {entities}
Similarity Score: {result["score"]:.4f}

{result["content"]}"""
            )

        return "\n\n".join(context_parts)