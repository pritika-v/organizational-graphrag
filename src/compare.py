import json
import time
from pathlib import Path

from .data_loader import load_data
from .neo4j_store import Neo4jStore
from .vector_store import PineconeVectorStore
from .graphrag import GraphRAG
from .vector_rag import VectorRAG


OUT = Path(__file__).resolve().parents[1] / 'outputs'
OUT.mkdir(exist_ok=True)


def call_with_retry(func, max_retries=4):
    """
    Run an LLM-backed function and retry if the provider
    temporarily rate-limits the request.
    """
    for attempt in range(max_retries):
        try:
            return func()

        except Exception as e:
            error_text = str(e)

            if "429" not in error_text and "rate_limit" not in error_text.lower():
                raise

            wait_time = 5 * (attempt + 1)

            print(
                f"\nRate limit reached. "
                f"Waiting {wait_time} seconds before retry "
                f"({attempt + 1}/{max_retries})..."
            )

            time.sleep(wait_time)

    raise RuntimeError(
        "The LLM provider continued returning rate-limit errors "
        "after multiple retries."
    )


def run():
    _, benchmark = load_data()

    neo = Neo4jStore()
    pine = PineconeVectorStore()

    graph = GraphRAG(neo)
    vector = VectorRAG(pine)

    results = []

    for index, item in enumerate(benchmark, start=1):

        print("\n" + "=" * 70)
        print(f"QUERY {index}/{len(benchmark)}")
        print(item['question'])
        print("=" * 70)

        # ---------------------------------------------------------
        # 1. GraphRAG retrieval
        # ---------------------------------------------------------
        print("\n[1/4] Running GraphRAG retrieval...")

        gr = call_with_retry(
            lambda: graph.retrieve(item['question'])
        )

        # Give the provider a small breathing window
        time.sleep(2)

        # ---------------------------------------------------------
        # 2. Vector RAG retrieval
        # ---------------------------------------------------------
        print("[2/4] Running Vector RAG retrieval...")

        vr = vector.retrieve(item['question'])

        # ---------------------------------------------------------
        # 3. Calculate retrieval metrics
        # ---------------------------------------------------------
        graph_ids = set(
            n['id']
            for n in gr['nodes']
        )

        vector_ids = set(
            x['id']
            for x in vr
        )

        expected = set(
            item['expected_nodes']
        )

        graph_recall = (
            len(expected & graph_ids) / len(expected)
            if expected else 0
        )

        vector_recall = (
            len(expected & vector_ids) / len(expected)
            if expected else 0
        )

        # ---------------------------------------------------------
        # 4. Generate GraphRAG answer
        # ---------------------------------------------------------
        print("[3/4] Generating GraphRAG answer...")

        graph_answer = call_with_retry(
            lambda: graph.answer(item['question'], gr)
        )

        time.sleep(5)

        # ---------------------------------------------------------
        # 5. Generate Vector RAG answer
        # ---------------------------------------------------------
        print("[4/4] Generating Vector RAG answer...")

        vector_answer = call_with_retry(
            lambda: vector.answer(item['question'], vr)
        )

        time.sleep(5)

        # ---------------------------------------------------------
        # Store results
        # ---------------------------------------------------------
        results.append({
            'id': item['id'],
            'question': item['question'],
            'type': item['type'],

            'expected_nodes': sorted(expected),

            'graph_nodes': sorted(graph_ids),
            'vector_nodes': sorted(vector_ids),

            'graph_recall': round(graph_recall, 3),
            'vector_recall': round(vector_recall, 3),

            'graph_relationships': gr['relationships'],

            'vector_scores': [
                {
                    k: v
                    for k, v in x.items()
                    if k in ['id', 'score', 'name', 'label']
                }
                for x in vr
            ],

            'graph_answer': graph_answer,
            'vector_answer': vector_answer
        })

        print(
            f"\nGraph recall:  {graph_recall:.3f}"
        )

        print(
            f"Vector recall: {vector_recall:.3f}"
        )

    # -------------------------------------------------------------
    # Save detailed results
    # -------------------------------------------------------------
    with open(
        OUT / 'comparison_results.json',
        'w',
        encoding='utf-8'
    ) as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # -------------------------------------------------------------
    # Calculate overall results
    # -------------------------------------------------------------
    graph_avg = (
        sum(x['graph_recall'] for x in results)
        / len(results)
    )

    vector_avg = (
        sum(x['vector_recall'] for x in results)
        / len(results)
    )

    summary = {
        'queries': len(results),

        'graph_average_entity_recall':
            round(graph_avg, 3),

        'vector_average_entity_recall':
            round(vector_avg, 3),

        'graph_wins':
            sum(
                x['graph_recall'] > x['vector_recall']
                for x in results
            ),

        'vector_wins':
            sum(
                x['vector_recall'] > x['graph_recall']
                for x in results
            ),

        'ties':
            sum(
                x['graph_recall'] == x['vector_recall']
                for x in results
            )
    }

    with open(
        OUT / 'summary.json',
        'w',
        encoding='utf-8'
    ) as f:
        json.dump(
            summary,
            f,
            indent=2
        )

    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        json.dumps(
            summary,
            indent=2
        )
    )

    neo.close()


if __name__ == '__main__':
    run()