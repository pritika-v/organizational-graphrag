import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_loader import load_data
from src.neo4j_store import Neo4jStore

if __name__ == '__main__':
    data, _ = load_data()
    store = Neo4jStore()
    store.reset()
    store.create_graph(data)
    print(f"Loaded {len(data['nodes'])} nodes and {len(data['relationships'])} relationships into Neo4j.")
    store.close()
