import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import *
from src.data_loader import load_data

print('Configuration check')
print('Neo4j:', NEO4J_URI)
print('Pinecone key configured:', bool(PINECONE_API_KEY))
print('OpenAI key configured:', bool(OPENAI_API_KEY))
org, benchmark = load_data()
print('Nodes:', len(org['nodes']))
print('Relationships:', len(org['relationships']))
print('Benchmark queries:', len(benchmark))
