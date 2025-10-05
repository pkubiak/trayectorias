from models import Impact
import typing as T

V = T.TypeVar('V')
def apply_impact(value: V, impact: Impact) -> V:
    if impact.key is not None:
        assert isinstance(value, dict), "Value must be a dict if impact.key is set"
        if impact.key not in value:
            value[impact.key] = 0
        if impact.operation == "set":
            value[impact.key] = impact.value
        elif impact.operation == "add":
            value[impact.key] += impact.value
        elif impact.operation == "sub":
            value[impact.key] -= impact.value
        return value
    if isinstance(value, list):
        if impact.operation == "set":
            if isinstance(impact.value, list):
                return impact.value
            return [impact.value]
        elif impact.operation == "add":
            if isinstance(impact.value, list):
                return list(set(value + impact.value))
            else:
                return list(set(value) | {impact.value})
        elif impact.operation == "sub":
            if isinstance(impact.value, list):
                return list(set(value) - set(impact.value))
            else:
                return list(set(value) - {impact.value})
    elif isinstance(value, dict) and "value" in value:
        if impact.operation == "set":
            return {"value": impact.value, "unit": value["unit"]}
        elif impact.operation == "add":
            return {"value": value["value"] + impact.value, "unit": value["unit"]}
        elif impact.operation == "sub":
            return {"value": value["value"] - impact.value, "unit": value["unit"]}
    elif isinstance(value, str):
        if impact.operation == "set":
            return impact.value
        elif impact.operation in ("add", "sub"):
            raise ValueError(f"Cannot apply operation {impact.operation} to string value")
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")