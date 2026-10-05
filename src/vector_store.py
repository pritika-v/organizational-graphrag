from .config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_CLOUD, PINECONE_REGION, TOP_K
from .embeddings import Embedder

class PineconeVectorStore:
    def __init__(self):
        if not PINECONE_API_KEY:
            raise RuntimeError('PINECONE_API_KEY is missing.')
        from pinecone import Pinecone, ServerlessSpec
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = PINECONE_INDEX_NAME
        self.embedder = Embedder()
        existing = [x['name'] if isinstance(x, dict) else x.name for x in self.pc.list_indexes()]
        if self.index_name not in existing:
            self.pc.create_index(name=self.index_name, dimension=self.embedder.dimension, metric='cosine', spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION))
        self.index = self.pc.Index(self.index_name)

    def upsert_nodes(self, nodes):
        texts = [self._text(n) for n in nodes]
        vectors = self.embedder.embed(texts)
        payload = []
        for n, v, text in zip(nodes, vectors, texts):
            payload.append({'id':n['id'], 'values':v, 'metadata':{'name':n.get('name',''),'label':n.get('label',''),'text':text}})
        self.index.upsert(vectors=payload)

    def query(self, question, top_k=TOP_K):
        vector = self.embedder.embed([question])[0]
        result = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return [{'id':m['id'], 'score':m['score'], **(m.get('metadata') or {})} for m in result['matches']]

    @staticmethod
    def _text(n):
        return ' | '.join(str(n.get(k,'')) for k in ['name','label','description','text','role','department','skills'])
