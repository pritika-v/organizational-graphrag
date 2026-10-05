from pydantic import BaseModel, Field

class LinkOutput(BaseModel):
    entity_names: list[str] = Field(default_factory=list)
    relation_types: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

class QueryResult(BaseModel):
    question: str
    answer: str
    retrieved_node_ids: list[str] = Field(default_factory=list)
    retrieved_relationships: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
