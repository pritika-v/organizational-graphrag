# GraphRAG vs Vector RAG — Comparison Analysis

## Executive summary

The benchmark contains 10 organizational questions. GraphRAG average expected-entity recall was **0.776**, while Vector RAG average expected-entity recall was **0.500** on this synthetic dataset.

These numbers describe this benchmark only. The dataset was intentionally designed around relationship-heavy organizational questions, so the experiment should be interpreted as a demonstration of retrieval behavior rather than a universal ranking of architectures.

## Query-by-query results

| ID | Question | Type | Graph recall | Vector recall |
|---|---|---|---:|---:|
| Q01 | Who worked on the last compliance audit and what tools did they use? | multi_hop | 1.000 | 0.333 |
| Q02 | What decisions were made about the pricing model and who approved them? | decision_chain | 1.000 | 0.600 |
| Q03 | Who owns the Customer 360 data pipelines and which technologies do they use? | multi_hop | 0.667 | 0.333 |
| Q04 | Which people approved the decision to use Pinecone for support copilot retrieval? | decision_chain | 1.000 | 0.750 |
| Q05 | What tools were used by the team responsible for the SOC2 audit evidence? | multi_hop | 0.429 | 0.286 |
| Q06 | Who approved the Snowflake decision, and what project was it for? | decision_chain | 0.800 | 0.400 |
| Q07 | Which people connected to pricing have financial modeling or pricing skills? | skill_graph | 0.600 | 0.600 |
| Q08 | Who worked on cloud cost optimization, what infrastructure tools were involved, and who approved the rightsizing policy? | multi_hop | 1.000 | 0.429 |
| Q09 | For the vendor risk assessment, which people covered security, compliance, and legal review? | multi_hop | 0.667 | 0.667 |
| Q10 | What was the approved enterprise pricing model, who approved it, and which document records the decision? | decision_chain | 0.600 | 0.600 |

## Interpretation

- Graph retrieval is especially useful when the answer requires explicit relationship traversal, such as person → project → tool or decision → approver → project.
- Vector retrieval is useful when relevant evidence is expressed as semantically similar prose and exact relationship traversal is not necessary.
- A production architecture can combine semantic retrieval with graph expansion: use vectors to find candidate entities/documents, then use graph traversal to enforce relationship-aware context.

## Limitations

- Synthetic dataset with 42 nodes and 70 relationships.
- Only 10 benchmark questions.
- Entity recall does not fully measure answer correctness, faithfulness, latency, or cost.
- Fixed two-hop traversal may miss valid answers that require deeper paths or may retrieve unnecessary context.
- The vector baseline intentionally flattens each graph node into one short document; chunking strategy can materially affect vector-RAG results.

## Suggested demo conclusion

GraphRAG is not a replacement for vector RAG in every workload. Its value becomes clear when organizational knowledge contains important explicit relationships—ownership, approval, project membership, tool usage, decisions and provenance—that should be traversed rather than inferred from semantic similarity alone.