from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

DATA_DIR = ROOT / 'data'

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'secretgraph')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'org-graphrag-demo')
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD', 'aws')
PINECONE_REGION = os.getenv('PINECONE_REGION', 'us-east-1')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5.1')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai').lower()
LOCAL_EMBEDDING_MODEL = os.getenv('LOCAL_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
TOP_K = int(os.getenv('TOP_K', '5'))
GRAPH_HOPS = int(os.getenv('GRAPH_HOPS', '2'))
USE_LLM_LINKER = os.getenv('USE_LLM_LINKER', 'true').lower() == 'true'
USE_LLM_ANSWER = os.getenv('USE_LLM_ANSWER', 'true').lower() == 'true'
