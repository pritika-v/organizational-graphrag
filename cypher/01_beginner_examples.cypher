// Run these one at a time in Neo4j Browser at http://localhost:7474

// 1. See every node
MATCH (n) RETURN n LIMIT 50;

// 2. See people
MATCH (p:Person) RETURN p.name, p.role, p.department;

// 3. See people and projects they worked on
MATCH (p:Person)-[:WORKED_ON]->(pr:Project)
RETURN p.name, pr.name;

// 4. Find the pricing decision and its approvers
MATCH (d:Decision {id:'DEC001'})-[:APPROVED_BY]->(p:Person)
RETURN d.name, p.name;

// 5. Follow a decision to its project and approvers
MATCH (d:Decision)-[:DECISION_FOR]->(pr:Project),
      (d)-[:APPROVED_BY]->(p:Person)
RETURN d.name, pr.name, collect(p.name) AS approvers;

// 6. Two-hop question: people -> project -> documents
MATCH (p:Person)-[:WORKED_ON]->(pr:Project)-[:HAS_DOCUMENT]->(doc:Document)
RETURN p.name, pr.name, doc.name;
