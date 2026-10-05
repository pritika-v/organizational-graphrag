# Organizational Knowledge GraphRAG: Graph vs Vector RAG

A beginner-friendly project that models organizational knowledge as a Neo4j graph and compares graph retrieval against Pinecone vector retrieval on the same 10 questions.

## What this project demonstrates

- 42 organizational nodes across people, projects, skills, tools, documents and decisions.
- Typed relationships such as `WORKED_ON`, `USED_TOOL`, `APPROVED_BY`, `DECISION_FOR`, `DOCUMENTED_IN`, `HAS_DOCUMENT`, `HAS_SKILL` and `AUTHORED`.
- GraphRAG pipeline: question -> entity/relation linking -> Neo4j seed nodes -> 2-hop subgraph -> document evidence -> LLM answer.
- Vector RAG pipeline: node text -> embeddings -> Pinecone -> top-k semantic retrieval -> LLM answer.
- 10 benchmark questions and entity-recall comparison.
- Streamlit demo.

## Architecture

```text
                         SAME MOCK ORGANIZATIONAL DATA
                                      |
                       +--------------+--------------+
                       |                             |
                 Neo4j Graph                    Flat Node Text
                       |                             |
             Entity + relation linking          Embeddings
                       |                             |
                 Seed nodes                    Pinecone
                       |                             |
                  2-hop Cypher                 Top-k vectors
                       |                             |
                 Subgraph + docs                Context
                       |                             |
                       +-------------+-------------+
                                     |
                                  LLM answer
                                     |
                           Comparison / benchmark
```

## Project structure

```text
organizational_graphrag/
├── app.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   ├── organization.json
│   └── benchmark.json
├── cypher/
│   └── 01_beginner_examples.cypher
├── scripts/
│   ├── seed_neo4j.py
│   ├── seed_pinecone.py
│   ├── query_graph.py
│   └── query_vector.py
├── src/
│   ├── config.py
│   ├── models.py
│   ├── data_loader.py
│   ├── neo4j_store.py
│   ├── linker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── graphrag.py
│   ├── vector_rag.py
│   └── compare.py
└── docs/
    └── IMPLEMENTATION_GUIDE.md
```

## Quick start

### 1. Requirements

- Windows 10/11
- VS Code
- Python 3.10+
- Docker Desktop
- A Pinecone account/API key
- An OpenAI API key if you want LLM answers and OpenAI embeddings

The Neo4j Python driver currently requires Python 3.10+ and supports current Neo4j releases. See the official Neo4j Python driver documentation for connection details.

### 2. Open the folder in VS Code

Extract the zip, then open the extracted `organizational_graphrag` folder in VS Code.

### 3. Create and activate a virtual environment

PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Create `.env`

Copy `.env.example` to `.env` and fill in:

```text
PINECONE_API_KEY=...
OPENAI_API_KEY=...
```

Keep the Neo4j defaults unchanged for the Docker setup.

### 5. Start Neo4j

From the project folder:

```powershell
docker compose up -d
```

Open http://localhost:7474 in your browser.

Login:

- username: `neo4j`
- password: `secretgraph`

### 6. Load the graph

```powershell
python scripts\seed_neo4j.py
```

Expected output is approximately:

```text
Loaded 42 nodes and 70 relationships into Neo4j.
```

### 7. Explore Neo4j/Cypher

In Neo4j Browser, try:

```cypher
MATCH (n) RETURN n LIMIT 50;
```

Then open `cypher/01_beginner_examples.cypher` and run the examples one at a time.

### 8. Load Pinecone

```powershell
python scripts\seed_pinecone.py
```

The script creates the Pinecone index if it does not already exist and indexes the same 44 nodes as flat text documents.

### 9. Test GraphRAG

```powershell
python scripts\query_graph.py "Who worked on the last compliance audit and what tools did they use?"
```

### 10. Test vector RAG

```powershell
python scripts\query_vector.py "Who worked on the last compliance audit and what tools did they use?"
```

### 11. Run the 10-query comparison

```powershell
python -m src.compare
```

Outputs:

```text
outputs/comparison_results.json
outputs/summary.json
```

The benchmark reports entity recall for each pipeline. It does not claim that one architecture is universally better; it measures this dataset and these questions.

### 12. Run the UI

```powershell
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Important environment options

### OpenAI embeddings

```text
EMBEDDING_PROVIDER=openai
```

This uses `text-embedding-3-small` by default.

### Local embeddings

If you want to avoid OpenAI embeddings:

```text
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

The first run downloads the local model. Pinecone index dimension is detected automatically from the model.

### Disable LLM answering

```text
USE_LLM_ANSWER=false
```

Retrieval still runs and the scripts print the retrieved entities. LLM entity linking is also optional; when disabled or when no OpenAI key is present, the project uses deterministic entity/topic shortcuts plus fuzzy matching.

## Why the comparison is fair

Both pipelines use exactly the same source dataset. The vector pipeline flattens every graph node into a short document. The graph pipeline preserves typed relationships. Therefore the experiment isolates retrieval strategy rather than giving one method more source information.

## What to show in the demo

1. Show the 44-node organizational dataset.
2. Open Neo4j Browser and run `MATCH (n) RETURN n LIMIT 50`.
3. Explain one relationship: `(Aisha)-[:WORKED_ON]->(SOC2 Audit)`.
4. Run the compliance-audit query through GraphRAG.
5. Show the seed node and 2-hop expansion.
6. Run the same query through vector RAG.
7. Explain that vector RAG sees semantic similarity, while GraphRAG can explicitly traverse person -> project -> tool and decision -> approver -> project.
8. Run the 10-query benchmark.
9. Show `outputs/summary.json` and 2-3 interesting query rows.
10. End with the limitations: small synthetic dataset, only 10 benchmark questions, fixed hop count, and retrieval metrics do not fully measure answer quality.

## Security note

This repository uses a local mock dataset. Do not upload confidential organizational data to external LLM/vector services without checking your organization's data handling requirements.
