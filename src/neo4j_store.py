from neo4j import GraphDatabase
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

class Neo4jStore:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def reset(self):
        self.driver.execute_query(
            "MATCH (n) DETACH DELETE n",
            database_=NEO4J_DATABASE,
        )

    def create_graph(self, data):
        # Labels and relationship types come from our controlled dataset, not user input.
        for node in data['nodes']:
            props = {k: v for k, v in node.items() if k != 'label'}
            label = node['label']
            query = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
            self.driver.execute_query(query, id=node['id'], props=props, database_=NEO4J_DATABASE)

        for rel in data['relationships']:
            query = f"""
            MATCH (a {{id: $source}}), (b {{id: $target}})
            MERGE (a)-[:{rel['type']}]->(b)
            """
            self.driver.execute_query(query, source=rel['source'], target=rel['target'], database_=NEO4J_DATABASE)

    def all_nodes(self):
        records, _, _ = self.driver.execute_query(
            "MATCH (n) RETURN n.id AS id, labels(n)[0] AS label, n.name AS name ORDER BY id",
            database_=NEO4J_DATABASE,
        )
        return [r.data() for r in records]

    def match_node_names(self, names):
        records, _, _ = self.driver.execute_query(
            "MATCH (n) WHERE any(name IN $names WHERE toLower(n.name) = toLower(name)) RETURN n.id AS id, n.name AS name",
            names=names,
            database_=NEO4J_DATABASE,
        )
        return [r.data() for r in records]

    def find_nodes_by_keyword(self, keywords):
        records, _, _ = self.driver.execute_query(
            """
            MATCH (n)
            WHERE any(k IN $keywords WHERE toLower(coalesce(n.name,'')) CONTAINS toLower(k)
                OR toLower(coalesce(n.description,'')) CONTAINS toLower(k)
                OR toLower(coalesce(n.text,'')) CONTAINS toLower(k))
            RETURN n.id AS id, n.name AS name, labels(n)[0] AS label
            LIMIT 20
            """,
            keywords=keywords,
            database_=NEO4J_DATABASE,
        )
        return [r.data() for r in records]

    def expand_subgraph(self, seed_ids, relation_types=None, hops=2):
        # We use variable-length paths up to the requested hop count. Relationship filtering
        # is generated only from a controlled allow-list supplied by the linker/benchmark.
        rel_clause = ''
        allowed = {'WORKED_ON','USED_TOOL','APPROVED_BY','DECISION_FOR','DOCUMENTED_IN','HAS_DOCUMENT','HAS_SKILL','AUTHORED'}
        if relation_types:
            safe_types = [r for r in relation_types if r in allowed]
            if safe_types:
                rel_clause = '|'.join(safe_types)
        pattern = f"[r{':' + rel_clause if rel_clause else ''}*1..{int(hops)}]"
        query = f"""
        MATCH (s)-{pattern}-(n)
        WHERE s.id IN $seed_ids
        WITH collect(DISTINCT s) + collect(DISTINCT n) AS nodes
        UNWIND nodes AS node
        OPTIONAL MATCH (node)-[r]-(other)
        WHERE other.id IN [x IN nodes | x.id]
        RETURN DISTINCT node.id AS id, labels(node)[0] AS label, node.name AS name,
               node.text AS text, node.description AS description,
               type(r) AS rel_type, other.id AS other_id, other.name AS other_name
        """
        records, _, _ = self.driver.execute_query(query, seed_ids=seed_ids, database_=NEO4J_DATABASE)
        rows = [r.data() for r in records]
        if not rows and relation_types:
            return self.expand_subgraph(seed_ids, relation_types=None, hops=hops)
        return rows
