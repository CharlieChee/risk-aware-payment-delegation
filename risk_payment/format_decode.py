"""Syntax-only carrier decoding. No expressions, attributes, models or labels.

Accept exactly one schema-valid instance; all other content must be an exact
echo of the declared schema. Never correct an expression or choose by score.
"""
import json

def decode(text,schema,validate):
    text=text.strip()
    if text.startswith('```json\n') and text.endswith('\n```'):
        text=text[len('```json\n'):-len('\n```')].strip()
    if len(text)>500000:raise ValueError('carrier_too_large')
    decoder=json.JSONDecoder();objects=[];offset=0
    while offset<len(text):
        while offset<len(text) and text[offset].isspace():offset+=1
        if offset==len(text):break
        obj,end=decoder.raw_decode(text,offset);objects.append(obj);offset=end
    if not objects:raise ValueError('no_json_value')
    found=[];steps=[]
    def visit(value,depth=0):
        if depth>3:raise ValueError('carrier_nesting_limit')
        if not validate(value,schema):
            found.append(value);steps.append('schema_valid_instance');return
        if value==schema:
            steps.append('exact_schema_echo');return
        if not isinstance(value,dict):raise ValueError('unrecognized_carrier')
        # Some providers/models concatenate schema metadata and instance keys.
        # Strip only metadata whose keys and values exactly equal the schema.
        # Never strip a key that is also an expected instance property.
        expected=set(schema.get('properties',{}));metadata=set(schema)
        if expected.isdisjoint(metadata) and all(k in value and value[k]==schema[k] for k in metadata):
            rest={k:v for k,v in value.items() if k not in metadata}
            if not validate(rest,schema):
                found.append(rest);steps.append('exact_schema_metadata_removed');return
            if len(rest)==1:
                steps.append('single_payload_wrapper');visit(next(iter(rest.values())),depth+1);return
        # Or schema and payload can be two explicitly separate siblings.
        echoes=[k for k,v in value.items() if v==schema]
        if len(echoes)==1 and len(value)==2:
            steps.append('schema_and_single_payload_wrapper')
            visit(next(v for k,v in value.items() if k!=echoes[0]),depth+1);return
        raise ValueError('unrecognized_carrier')
    for value in objects:visit(value)
    unique={json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')):x for x in found}
    if len(unique)!=1:raise ValueError('no_unique_schema_instance')
    return next(iter(unique.values())),dict(steps=steps,objects=len(objects),instances=len(found),unique_instances=1,
                                        expressions_edited=False,reference_access=False)
