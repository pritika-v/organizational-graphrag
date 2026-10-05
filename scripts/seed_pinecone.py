import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_loader import load_data
from src.vector_store import PineconeVectorStore

if __name__ == '__main__':
    data, _ = load_data()
    store = PineconeVectorStore()
    store.upsert_nodes(data['nodes'])
    print(f"Indexed {len(data['nodes'])} organizational nodes in Pinecone.")
