from .linker import EntityLinker
from .config import GRAPH_HOPS, OPENAI_API_KEY, OPENAI_MODEL, USE_LLM_ANSWER

class GraphRAG:
    def __init__(self, store):
        self.store = store
        self.linker = EntityLinker(store)
        self.client = None
        if USE_LLM_ANSWER and OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY,base_url="https://api.groq.com/openai/v1")

    def retrieve(self, question):
        link, seeds = self.linker.link(question)
        rows = self.store.expand_subgraph(seeds, link.relation_types, GRAPH_HOPS)
        node_map = {}
        relationships = []

        for row in rows:
            if row.get('id'):
                node_map[row['id']] = {
                    k: row.get(k)
                    for k in ['id', 'label', 'name', 'text', 'description']
                }

            if row.get('rel_type') and row.get('other_id'):
                source_name = row.get('name') or row.get('id')
                target_name = row.get('other_name') or row.get('other_id')

                relationships.append(
                    f"{source_name} -[{row['rel_type']}]-> {target_name}"
                )
        return {'link':link, 'seed_ids':seeds, 'nodes':list(node_map.values()), 'relationships':list(dict.fromkeys(relationships))}

    def answer(self, question, retrieved):
        if not self.client:
            names = ', '.join(n['name'] for n in retrieved['nodes'] if n.get('name'))
            return f"LLM answering is disabled. Retrieved graph entities: {names}."
        graph_facts = '\n'.join(retrieved['relationships'])
        docs = '\n'.join(n.get('text') or n.get('description') or '' for n in retrieved['nodes'] if n.get('text') or n.get('description'))
        prompt = f"""Answer the organizational knowledge question using the graph facts as the primary source of truth. Use document text only for supporting detail. Name every relevant person, project, tool and decision. If the context is insufficient, say so.\n\nQUESTION:\n{question}\n\nGRAPH FACTS:\n{graph_facts}\n\nDOCUMENT EVIDENCE:\n{docs}"""
        response = self.client.responses.create(model=OPENAI_MODEL, input=prompt)
        return response.output_text
