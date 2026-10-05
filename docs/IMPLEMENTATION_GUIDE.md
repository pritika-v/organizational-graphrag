# Implementation Guide: Neo4j, Cypher, GraphRAG and the Comparison

## 1. First understand the graph idea

A vector database answers questions by comparing meaning. A graph database answers questions by following explicit relationships.

For this project:

```text
Aisha Raman --WORKED_ON--> SOC2 Compliance Audit --HAS_DOCUMENT--> SOC2 Evidence Tracker
Aisha Raman --USED_TOOL--> Jira
Kavya Shah --WORKED_ON--> SOC2 Compliance Audit
Kavya Shah --USED_TOOL--> AWS
DEC004 --DECISION_FOR--> SOC2 Compliance Audit
DEC004 --APPROVED_BY--> Aisha Raman
```

A question such as “Who worked on the audit and what tools did they use?” requires joining several facts. That is exactly the kind of query the graph structure makes explicit.

## 2. Neo4j in one minute

Neo4j is a graph database. Instead of storing everything as rows and joins, it stores:

- **Nodes**: entities such as people, projects and tools.
- **Relationships**: typed connections between nodes.
- **Properties**: attributes on nodes or relationships.

Example:

```text
(:Person {name: "Aisha Raman"})
    -[:WORKED_ON]->
(:Project {name: "SOC2 Compliance Audit"})
```

The square brackets contain the relationship type. The arrows show direction.

## 3. What is Cypher?

Cypher is Neo4j's query language. It is similar in spirit to SQL, but instead of thinking primarily in tables, you describe graph patterns.

SQL-style thinking:

```text
find rows in Person
join with Project
join with Tool
```

Cypher-style thinking:

```cypher
MATCH (p:Person)-[:WORKED_ON]->(pr:Project)-[:HAS_DOCUMENT]->(d:Document)
RETURN p.name, pr.name, d.name;
```

Read the pattern from left to right:

1. Find a Person node and call it `p`.
2. Follow a `WORKED_ON` relationship.
3. Arrive at a Project node called `pr`.
4. Follow `HAS_DOCUMENT`.
5. Arrive at a Document node called `d`.
6. Return their names.

## 4. The five Cypher commands you need for this project

### MATCH = find

```cypher
MATCH (p:Person)
RETURN p;
```

### CREATE = create

```cypher
CREATE (p:Person {name:'Demo Person'})
RETURN p;
```

### MERGE = create if missing / match if present

The Python loader uses `MERGE` so repeated seeding does not create duplicate nodes with the same ID.

### WHERE = filter

```cypher
MATCH (p:Person)
WHERE p.department = 'Security'
RETURN p.name;
```

### RETURN = choose output

```cypher
MATCH (p:Person)-[:WORKED_ON]->(pr:Project)
RETURN p.name, pr.name;
```

## 5. Why relationships matter

Consider:

> Who approved the pricing decision, and what project was it for?

The graph can directly represent:

```text
Decision
  |--APPROVED_BY--> Person
  |--DECISION_FOR--> Project
```

A Cypher query is:

```cypher
MATCH (d:Decision)-[:APPROVED_BY]->(p:Person),
      (d)-[:DECISION_FOR]->(pr:Project)
WHERE d.id = 'DEC001'
RETURN d.name, collect(p.name) AS approvers, pr.name;
```

This is a multi-hop retrieval problem, not just a text-similarity problem.

## 6. How the GraphRAG pipeline works

### Step A — User question

Example:

```text
Who worked on the last compliance audit and what tools did they use?
```

### Step B — Entity/relation linking

The linker identifies concepts such as:

```text
entity: SOC2 Compliance Audit
relations: WORKED_ON, USED_TOOL
```

When an OpenAI key is available, the linker asks the model for structured JSON conforming to a schema. Pydantic validates that JSON. Without the key, deterministic shortcuts and fuzzy matching are used.

### Step C — Seed nodes

The linked entity is matched to its Neo4j node ID:

```text
SOC2 Compliance Audit -> PR001
```

This node becomes a seed.

### Step D — Subgraph expansion

The code asks Neo4j for paths up to two relationships away.

Conceptually:

```text
PR001
 |
 +-- WORKED_ON -- P001 Aisha
 |                 |
 |                 +-- USED_TOOL -- Jira
 |
 +-- WORKED_ON -- P005 Kavya
                   |
                   +-- USED_TOOL -- AWS
                   +-- USED_TOOL -- Datadog
```

If a relation filter is too restrictive and returns nothing, the code retries without the relation filter.

### Step E — Document evidence

Document nodes such as `SOC2 Evidence Tracker` and `Audit Readiness Runbook` can be attached to the retrieved context. Their full text gives the LLM supporting prose.

### Step F — Answer generation

The prompt tells the LLM:

- graph facts are primary;
- document text is supporting evidence;
- name relevant entities;
- say when evidence is insufficient.

## 7. How Vector RAG works in this project

The exact same node data is flattened.

Example:

```text
SOC2 Compliance Audit | Project | Annual SOC2 Type II readiness...
```

That text is embedded and stored in Pinecone.

At query time:

```text
question
  -> embedding
  -> Pinecone similarity search
  -> top 5 nodes
  -> LLM
```

The vector system does not inherently know that a particular person worked on a particular project or that a decision was approved by someone. It only retrieves text whose embedding is close to the query.

## 8. What the 10-query benchmark measures

For each query, the benchmark has an expected set of relevant node IDs.

For example:

```text
Expected:
P001, P005, PR001, T001, T003, T004
```

If a system retrieves four of those six nodes:

```text
entity recall = 4 / 6 = 0.667
```

This is deliberately simple and transparent. The project also saves the actual retrieved relationships and generated answers so you can manually inspect quality.

## 9. How to interpret results

Do not treat the benchmark as a universal scientific proof. The dataset is synthetic and intentionally designed to contain relationship-heavy questions.

Use the results to discuss:

### GraphRAG tends to be useful when

- the answer requires traversing multiple explicit relationships;
- you need exact relationship types;
- you need provenance such as who approved a decision;
- entities have short or ambiguous names;
- the question asks for connected sets of entities.

### Vector RAG tends to be useful when

- the query is primarily about topical similarity;
- relevant information is expressed in natural-language passages;
- exact graph structure is not available or expensive to maintain;
- you want a simpler ingestion pipeline.

### Hybrid systems are often practical

A production system can combine both:

```text
semantic retrieval -> identify candidate entities
                         |
                         v
                    graph expansion
                         |
                         v
                 relationship-aware context
```

## 10. Beginner troubleshooting

### `python is not recognized`

Use:

```powershell
py --version
```

If `py` works, create the environment with `py -3.11 -m venv .venv`.

### Docker is not running

Open Docker Desktop and wait until it says Docker is running. Then:

```powershell
docker compose up -d
```

Check:

```powershell
docker ps
```

### Neo4j connection refused

Check:

```powershell
docker ps
```

The container should expose ports 7474 and 7687.

### Neo4j password error

For this project the default is:

```text
username: neo4j
password: secretgraph
```

If you changed the Docker credentials, update `.env` accordingly.

### Pinecone errors

Check `PINECONE_API_KEY`. Also make sure the region/cloud in `.env` is supported by your Pinecone account. If an index already exists with the same name but a different dimension, use a new index name.

### OpenAI errors

Check `OPENAI_API_KEY` and `OPENAI_MODEL`. You can set `USE_LLM_ANSWER=false` to test retrieval without generating answers.

### Local embedding model takes time

The first run downloads the model. Later runs use the local cache. This is only relevant when `EMBEDDING_PROVIDER=local`.

## 11. Suggested demo narration

“Here I have the same organizational dataset represented in two ways. Neo4j stores explicit entities and typed relationships, while Pinecone receives a flattened text representation of those same nodes. I ask the same ten questions to both systems. The graph pipeline first links the question to seed entities, then traverses the graph up to two hops and attaches document evidence. The vector pipeline performs semantic top-k retrieval. The benchmark measures which expected entities each method retrieved. This lets us demonstrate that GraphRAG is valuable when the answer depends on relationships, not merely topic similarity.”
