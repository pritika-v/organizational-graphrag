import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sys
from src.neo4j_store import Neo4jStore
from src.graphrag import GraphRAG

q = ' '.join(sys.argv[1:]) or 'Who worked on the last compliance audit and what tools did they use?'
store = Neo4jStore(); rag = GraphRAG(store)
r = rag.retrieve(q)
print('\nSEEDS:', r['seed_ids'])
print('\nNODES:')
for n in r['nodes']: print(n['id'], '|', n['label'], '|', n['name'])
print('\nRELATIONSHIPS:')
for rel in r['relationships']: print(rel)
print('\nANSWER:\n', rag.answer(q, r))
store.close()
