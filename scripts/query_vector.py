import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sys
from src.vector_store import PineconeVectorStore
from src.vector_rag import VectorRAG

q = ' '.join(sys.argv[1:]) or 'Who worked on the last compliance audit and what tools did they use?'
store = PineconeVectorStore(); rag = VectorRAG(store)
hits = rag.retrieve(q)
for h in hits: print(h['id'], '|', h.get('label'), '|', h.get('name'), '| score=', round(h['score'],4))
print('\nANSWER:\n', rag.answer(q, hits))
