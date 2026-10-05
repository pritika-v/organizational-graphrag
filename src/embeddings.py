from .config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, EMBEDDING_PROVIDER, LOCAL_EMBEDDING_MODEL

class Embedder:
    def __init__(self):
        self.provider = EMBEDDING_PROVIDER
        self.client = None
        self.model = None
        if self.provider == 'openai':
            if not OPENAI_API_KEY:
                raise RuntimeError('EMBEDDING_PROVIDER=openai but OPENAI_API_KEY is missing.')
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(LOCAL_EMBEDDING_MODEL)

    @property
    def dimension(self):
        if self.provider == 'openai':
            return 1536 if 'text-embedding-3-small' in OPENAI_EMBEDDING_MODEL else 3072
        return self.model.get_sentence_embedding_dimension()

    def embed(self, texts):
        if self.provider == 'openai':
            return [x.embedding for x in self.client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=texts).data]
        return self.model.encode(texts, normalize_embeddings=True).tolist()
