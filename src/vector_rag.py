from .config import OPENAI_API_KEY, OPENAI_MODEL, USE_LLM_ANSWER

class VectorRAG:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.client = None
        if USE_LLM_ANSWER and OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY,base_url="https://api.groq.com/openai/v1")

    def retrieve(self, question, top_k=5):
        return self.vector_store.query(question, top_k=top_k)

    def answer(self, question, hits):
        context = '\n'.join(f"[{h['id']}] {h.get('text','')}" for h in hits)
        if not self.client:
            return 'LLM answering is disabled. Retrieved vector documents: ' + ', '.join(h['id'] for h in hits)
        prompt = f"Answer only from the retrieved organizational documents. If the evidence is insufficient, say so.\n\nQUESTION:\n{question}\n\nRETRIEVED DOCUMENTS:\n{context}"
        response = self.client.responses.create(model=OPENAI_MODEL, input=prompt)
        return response.output_text
