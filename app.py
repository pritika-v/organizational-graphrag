import streamlit as st
from src.neo4j_store import Neo4jStore
from src.graphrag import GraphRAG
from src.vector_store import PineconeVectorStore
from src.vector_rag import VectorRAG

st.set_page_config(page_title='Organizational GraphRAG', layout='wide')
st.title('Organizational Knowledge: GraphRAG vs Vector RAG')
st.caption('Neo4j graph traversal compared with Pinecone semantic retrieval')

q = st.text_input('Ask a question', 'Who worked on the last compliance audit and what tools did they use?')

if st.button('Run both pipelines'):
    with st.spinner('Querying Neo4j and Pinecone...'):
        neo = Neo4jStore(); gr = GraphRAG(neo)
        pine = PineconeVectorStore(); vr = VectorRAG(pine)
        graph = gr.retrieve(q); vector = vr.retrieve(q)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader('GraphRAG')
        st.write(gr.answer(q, graph))
        st.markdown('**Seeds**')
        st.write(graph['seed_ids'])
        st.markdown('**Retrieved entities**')
        st.write([n['name'] for n in graph['nodes']])
        st.markdown('**Relationships**')
        for r in graph['relationships']:
            st.code(r)
    with c2:
        st.subheader('Vector RAG')
        st.write(vr.answer(q, vector))
        st.markdown('**Top Pinecone matches**')
        for h in vector:
            st.write(f"{h['name']} — score {h['score']:.3f}")
    neo.close()
