import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'

summary = json.load(open(OUT/'summary.json', encoding='utf-8'))
results = json.load(open(OUT/'comparison_results.json', encoding='utf-8'))

lines = [
    '# GraphRAG vs Vector RAG — Comparison Analysis',
    '',
    '## Executive summary',
    '',
    f"The benchmark contains {summary['queries']} organizational questions. GraphRAG average expected-entity recall was **{summary['graph_average_entity_recall']:.3f}**, while Vector RAG average expected-entity recall was **{summary['vector_average_entity_recall']:.3f}** on this synthetic dataset.",
    '',
    'These numbers describe this benchmark only. The dataset was intentionally designed around relationship-heavy organizational questions, so the experiment should be interpreted as a demonstration of retrieval behavior rather than a universal ranking of architectures.',
    '',
    '## Query-by-query results',
    '',
    '| ID | Question | Type | Graph recall | Vector recall |',
    '|---|---|---|---:|---:|'
]
for r in results:
    lines.append(f"| {r['id']} | {r['question']} | {r['type']} | {r['graph_recall']:.3f} | {r['vector_recall']:.3f} |")

lines += ['', '## Interpretation', '',
'- Graph retrieval is especially useful when the answer requires explicit relationship traversal, such as person → project → tool or decision → approver → project.',
'- Vector retrieval is useful when relevant evidence is expressed as semantically similar prose and exact relationship traversal is not necessary.',
'- A production architecture can combine semantic retrieval with graph expansion: use vectors to find candidate entities/documents, then use graph traversal to enforce relationship-aware context.',
'', '## Limitations', '',
'- Synthetic dataset with 42 nodes and 70 relationships.',
'- Only 10 benchmark questions.',
'- Entity recall does not fully measure answer correctness, faithfulness, latency, or cost.',
'- Fixed two-hop traversal may miss valid answers that require deeper paths or may retrieve unnecessary context.',
'- The vector baseline intentionally flattens each graph node into one short document; chunking strategy can materially affect vector-RAG results.',
'', '## Suggested demo conclusion', '',
'GraphRAG is not a replacement for vector RAG in every workload. Its value becomes clear when organizational knowledge contains important explicit relationships—ownership, approval, project membership, tool usage, decisions and provenance—that should be traversed rather than inferred from semantic similarity alone.'
]

open(OUT/'comparison_analysis.md','w',encoding='utf-8').write('\n'.join(lines))
print('Wrote outputs/comparison_analysis.md')
