import json
import re
from rapidfuzz import process, fuzz
from .models import LinkOutput
from .config import OPENAI_API_KEY, OPENAI_MODEL, USE_LLM_LINKER

RELATIONS = ['WORKED_ON','USED_TOOL','APPROVED_BY','DECISION_FOR','DOCUMENTED_IN','HAS_DOCUMENT','HAS_SKILL','AUTHORED']

class EntityLinker:
    def __init__(self, neo4j_store):
        self.store = neo4j_store
        self.client = None
        if USE_LLM_LINKER and OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY,base_url="https://api.groq.com/openai/v1")
    
    def llm_link(self, question):
        schema = {
            'type':'object','properties':{
                'entity_names':{'type':'array','items':{'type':'string'}},
                'relation_types':{'type':'array','items':{'type':'string','enum':RELATIONS}},
                'keywords':{'type':'array','items':{'type':'string'}}
            },
            'required':['entity_names','relation_types','keywords'],'additionalProperties':False
        }
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Extract organization graph entities and relation types. '
                        'Only use relation types from the supplied schema. '
                        'Return concise entity names. '
                        'Return only valid JSON.'
                    )
                },
                {
                    'role': 'user',
                    'content': question
                }
            ],
            response_format={
                'type': 'json_schema',
                'json_schema': {
                    'name': 'graph_link',
                    'strict': True,
                    'schema': schema
                }
            }
        )

        content = response.choices[0].message.content

        return LinkOutput.model_validate(json.loads(content))
    def deterministic_link(self, question):
        nodes = self.store.all_nodes()
        names = [n['name'] for n in nodes]
        q_lower = question.lower()
        entity_names = []
        for name in names:
            if name.lower() in q_lower:
                entity_names.append(name)
        shortcuts = {
            'audit':['SOC2 Compliance Audit'], 'soc2':['SOC2 Compliance Audit'],
            'pricing':['Pricing Revamp 2026','Adopt hybrid enterprise pricing'],
            'customer 360':['Customer 360 Platform','Use Snowflake as Customer 360 warehouse'],
            'snowflake':['Use Snowflake as Customer 360 warehouse','Customer 360 Platform'],
            'pinecone':['Use Pinecone for support copilot retrieval','AI Support Copilot'],
            'support copilot':['AI Support Copilot','Use Pinecone for support copilot retrieval'],
            'cost optimization':['Cloud Cost Optimization','Introduce AWS rightsizing policy'],
            'rightsizing':['Introduce AWS rightsizing policy','Cloud Cost Optimization'],
            'vendor risk':['Vendor Risk Assessment']
        }
        for key, vals in shortcuts.items():
            if key in q_lower:
                entity_names.extend(vals)
        entity_names = list(dict.fromkeys(entity_names))
        relation_types = []
        if any(x in q_lower for x in ['worked','team','people','who','owner']): relation_types.append('WORKED_ON')
        if 'tool' in q_lower or 'technology' in q_lower or 'technologies' in q_lower or 'infrastructure' in q_lower: relation_types.append('USED_TOOL')
        if 'approved' in q_lower or 'approv' in q_lower: relation_types.append('APPROVED_BY')
        if 'decision' in q_lower or 'approved' in q_lower: relation_types.append('DECISION_FOR')
        if 'document' in q_lower or 'records' in q_lower: relation_types.append('DOCUMENTED_IN')
        if 'skill' in q_lower or 'skills' in q_lower: relation_types.append('HAS_SKILL')
        return LinkOutput(entity_names=list(dict.fromkeys(entity_names)), relation_types=list(dict.fromkeys(relation_types)), keywords=[])

    def link(self, question):
        linked = self.llm_link(question) if self.client else self.deterministic_link(question)
        exact = self.store.match_node_names(linked.entity_names)
        seed_ids = [x['id'] for x in exact]
        if not seed_ids:
            # Fuzzy matching against all node names, with a conservative threshold.
            nodes = self.store.all_nodes()
            choices = {n['name']: n['id'] for n in nodes}
            for name in linked.entity_names:
                match = process.extractOne(name, choices.keys(), scorer=fuzz.token_set_ratio)
                if match and match[1] >= 80:
                    seed_ids.append(choices[match[0]])
        if not seed_ids:
            # Deterministic topic fallback.
            hits = self.store.find_nodes_by_keyword(re.findall(r"[A-Za-z0-9]+", question))
            seed_ids = [h['id'] for h in hits[:5]]
        return linked, list(dict.fromkeys(seed_ids))
