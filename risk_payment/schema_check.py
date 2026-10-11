"""Unchanged syntax-only validator extracted from vendor/scoring_core.py.
No grading functions or reference access.
"""
def validate_schema(value, schema, path='$'):
    """Small validator for the exact closed schemas used by this experiment."""
    kind = schema['type']
    if isinstance(kind, list):
        if value is None and 'null' in kind: return []
        return validate_schema(value, {**schema, 'type': next(k for k in kind if k != 'null')}, path)
    expected = {'object': dict, 'array': list, 'string': str, 'boolean': bool}.get(kind)
    if expected is not None and type(value) is not expected: return [f'{path}: expected {kind}']
    errors = []
    if 'enum' in schema and value not in schema['enum']: errors.append(f'{path}: enum mismatch')
    if kind == 'object':
        for key in schema['required']:
            if key not in value: errors.append(f'{path}: missing {key}')
        if schema.get('additionalProperties') is False:
            for key in value:
                if key not in schema['properties']: errors.append(f'{path}: additional {key}')
        for key, child in schema['properties'].items():
            if key in value: errors += validate_schema(value[key], child, path + '.' + key)
    if kind == 'array':
        for i, child in enumerate(value): errors += validate_schema(child, schema['items'], f'{path}[{i}]')
    return errors
