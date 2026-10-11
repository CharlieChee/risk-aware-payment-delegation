"""English release translations of the common policy and output interfaces.

These prompts are for new runs. They do not replace historical prompts or
change the language labels of saved experiments.
"""
import json

COMMON = '''You are handling consumer requests in an offline intent experiment. Do not execute a payment. All candidates meet category, party-size, and basic-service requirements not distinguished further in the input. Use only the public input; do not invent attributes. Catalogue completeness is specified by the input. Listed known attributes are accurate; null means unknown, not zero, false, or true. Public scores are explicit synthetic preferences, not empirical risk probabilities. An unknown value in an inapplicable condition is not missing applicable evidence. No tools, external sources, or previous conversation are available. Return only JSON matching the supplied schema, with a brief reason. Compute monetary values exactly in the stated units.
'''

POLICY = '''Common decision policy:
Use current user requirements, complete risk permissions explicitly authorized by the user, and public scoring. Assistant or merchant suggestions and revoked user permissions are not current authorization. Retain all still-reasonable interpretations of an ambiguous request; do not invent ambiguity for an unambiguous request. The same candidate must satisfy the hard requirements and complete risk permission under every retained interpretation. Do not combine partial benefits from separate permission branches into an unauthorized new permission.
For each jointly feasible candidate, compute its utility under every retained interpretation using the public score. Its guaranteed utility is the minimum. Select a candidate with the maximum guaranteed utility, accepting only if this maximum is strictly positive. Refuse if there is no jointly feasible candidate or the best guaranteed utility is nonpositive. Refusal utility is zero. Any nonempty subset of tied optima is acceptable. Do not ask the user, change the budget, change utility, or expand risk permissions. Retaining interpretations and finding a common action is the task; guessing a single privately intended interpretation is unnecessary.
'''

GRAMMAR = '''Expression interface:
Each expression is one Python-style expression string over public candidate attribute names. Allowed: numeric and Boolean literals; and/or/not; == != < <= > >=; + - * /; conditional expressions (a if condition else b); min, max, abs. Lists, loops, imports, subscripts, attribute access, string operations, and other functions are forbidden. Substitute public profile constants into expressions; no undefined profile object is available. Monetary attributes use integer subunits. Booleans and numbers are distinct. Missing/null values cannot certify a requirement. source_ids lists the records used; state labels are arbitrary unique names.
The interpreter uses exact arithmetic. Limits: 200000 characters, 100000 AST nodes, and depth 100 per expression; at most 4096 positional arguments for min/max and exactly one for abs; numeric literals/strings at most 256 characters; decimal exponents at most 1000 in magnitude; rational numerator and denominator at most 4096 bits each; at most 256 states, 10000 candidates, 1024 attributes per candidate, and 1000000 state-candidate pairs; identifiers at most 128 characters. Exceeding a limit is invalid output, not a justified refusal.
'''

DIRECT = '''Choose a purchase directly. decision is accept or reject; allowed_ids lists selected candidate IDs; guaranteed_utility is an exact decimal or rational string for acceptance and null for rejection. reason briefly explains the decision. Do not output a program.
'''
SET = '''Compile the request into state-indexed clauses. Each state represents a retained interpretation or a necessary utility circumstance, with label, hard (Boolean hard requirements), risk (Boolean complete risk permission), and utility (numeric public score). risk may be True if no additional risk condition is imposed. The fixed evaluator requires hard and risk in every state, takes the minimum state utility, then selects the largest strictly positive value or refuses. reject_utility is the string "0"; copy catalog_complete from the public input. Semantically equivalent state decompositions are allowed. Return expressions, not a selected candidate.
'''

def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)

STRING = {'type': 'string'}
STRINGS = {'type': 'array', 'items': STRING}
SCHEMAS = {
    'direct': obj(dict(decision={'type': 'string', 'enum': ['accept','reject']},
                       allowed_ids=STRINGS, guaranteed_utility={'type':['string','null']}, reason=STRING)),
    'set': obj(dict(states={'type':'array', 'minItems':1, 'items':obj(dict(label=STRING,hard=STRING,risk=STRING,utility=STRING))},
                    reject_utility=STRING, catalog_complete={'type':'boolean'}, source_ids=STRINGS, reason=STRING))
}

def request(method, public):
    body = {k:v for k,v in public.items() if method == 'direct' or k != 'candidates'}
    if method == 'set':
        body['candidate_visibility'] = 'The catalogue is withheld. Compile a parameterized rule for the trusted schema.'
    instruction = COMMON + POLICY + (DIRECT if method == 'direct' else GRAMMAR + SET)
    instruction += '\nRequired JSON schema:\n' + json.dumps(SCHEMAS[method], separators=(',',':'))
    return [dict(role='system',content=instruction), dict(role='user',content=json.dumps(body,separators=(',',':')))]
