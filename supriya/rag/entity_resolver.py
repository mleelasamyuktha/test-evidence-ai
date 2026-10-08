# from config.entity_catalog import ENTITY_CATALOG


# class EntityResolver:

#     def resolve(self, entities):
#         resolved_tables = {}

#         for entity in entities:
#             entity = entity.lower().strip()

#             if entity in ENTITY_CATALOG:
#                 resolved_tables[entity] = ENTITY_CATALOG[entity]["table"]

#         return resolved_tables

#     def resolve_from_results(self, results):
#         entities = set()

#         for result in results:
#             for entity in result.get("entities", []):
#                 entities.add(entity.lower().strip())

#         return self.resolve(entities)

from config.entity_catalog import ENTITY_CATALOG


class EntityResolver:

    def resolve(self, entities):
        resolved_tables = {}

        for entity in entities:
            entity = entity.lower().strip()

            if entity in ENTITY_CATALOG:
                resolved_tables[entity] = ENTITY_CATALOG[entity]["table"]

        return resolved_tables

    def resolve_from_results(self, results):
        entities = set()

        for result in results:
            for entity in result.get("entities", []):
                entities.add(entity.lower().strip())

        return self.resolve(entities)

    def resolve_from_text(self, text):
        entities = set()
        text_lower = text.lower()

        for entity in ENTITY_CATALOG:
            if entity in text_lower:
                entities.add(entity)

        return self.resolve(entities)