Benchmark output files are created after running:

    python -m src.compare
    python scripts/make_report.py

They are intentionally not pre-generated because the results depend on your Pinecone index, embedding provider, retrieval settings and LLM configuration.
