"""Base class for agent tools."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Abstract base class for agent tools.
    
    Tools are capabilities that the agent can use to interact with
    the environment, such as reading files, executing commands, etc.
    """
    
    _TYPE_MAP = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calls."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters.
        
        Returns:
            String result of the tool execution.
        """
        pass

    def validate_params(self, params: dict[str, Any]) -> list[str]:
        """
        Lightweight JSON schema validation for tool parameters.

        Returns a list of error strings (empty if valid).
        Unknown params are ignored.
        """
        schema = self.parameters or {}

        # Default to an object schema if type is missing, and fail fast on unsupported top-level types.
        if "type" not in schema:
            schema = {"type": "object", **schema}
        elif schema.get("type") != "object":
            raise ValueError(
                f"Tool parameter schemas must have top-level type 'object'; got {schema.get('type')!r}"
            )

        return self._validate_schema(params, schema, path="")

    def _validate_schema(self, value: Any, schema: dict[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        expected_type = schema.get("type")
        label = path or "parameter"

        if expected_type in self._TYPE_MAP and not isinstance(value, self._TYPE_MAP[expected_type]):
            return [f"{label} should be {expected_type}"]

        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{label} must be one of {schema['enum']}")

        if expected_type in ("integer", "number"):
            if "minimum" in schema and value < schema["minimum"]:
                errors.append(f"{label} must be >= {schema['minimum']}")
            if "maximum" in schema and value > schema["maximum"]:
                errors.append(f"{label} must be <= {schema['maximum']}")

        if expected_type == "string":
            if "minLength" in schema and len(value) < schema["minLength"]:
                errors.append(f"{label} must be at least {schema['minLength']} chars")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                errors.append(f"{label} must be at most {schema['maxLength']} chars")

        if expected_type == "object":
            properties = schema.get("properties", {})
            for key in schema.get("required", []):
                if key not in value:
                    errors.append(f"missing required {path}.{key}" if path else f"missing required {key}")
            for key, item in value.items():
                if key in properties:
                    errors.extend(self._validate_schema(item, properties[key], f"{path}.{key}" if path else key))

        if expected_type == "array":
            items_schema = schema.get("items")
            if items_schema:
                for idx, item in enumerate(value):
                    errors.extend(self._validate_schema(item, items_schema, f"{path}[{idx}]" if path else f"[{idx}]"))

        return errors
    
    def to_schema(self) -> dict[str, Any]:
        """Convert tool to OpenAI function schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
