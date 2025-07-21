import json
from jsonschema import validate, ValidationError

def infer_schema(data):
    """
    Infere um esquema JSON básico a partir dos dados.
    """
    if isinstance(data, dict):
        properties = {key: infer_schema(value) for key, value in data.items()}
        return {"type": "object", "properties": properties}
    elif isinstance(data, list):
        if data:
            items = infer_schema(data[0])
        else:
            items = {}
        return {"type": "array", "items": items}
    elif isinstance(data, str):
        return {"type": "string"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif data is None:
        return {"type": "null"}
    else:
        return {}

def validate_json_schema(file_path, schema=None):
    """
    Valida um arquivo JSON contra um esquema ou infere um esquema.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "errors": f"Invalid JSON file: {e}",
            "inferred_schema": None
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": str(e),
            "inferred_schema": None
        }

    inferred_schema = None
    if schema:
        try:
            validate(instance=data, schema=schema)
            return {
                "status": "valid",
                "errors": None,
                "inferred_schema": None
            }
        except ValidationError as e:
            return {
                "status": "invalid",
                "errors": str(e),
                "inferred_schema": None
            }
    else:
        inferred_schema = infer_schema(data)
        return {
            "status": "schema_inferred",
            "errors": None,
            "inferred_schema": inferred_schema
        }
