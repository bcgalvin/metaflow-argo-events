import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class ParameterNameReservedError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Parameter name '{name}' is a reserved word")


class UnsupportedParameterTypeError(ValueError):
    def __init__(self, type_name: str) -> None:
        super().__init__(f"Unsupported parameter type: {type_name}")


class SeparatorTypeError(ValueError):
    def __init__(self) -> None:
        super().__init__("Separator can only be used with string type parameters")


class InvalidJSONStringError(ValueError):
    def __init__(self) -> None:
        super().__init__("Invalid JSON string")


class InvalidJSONTypeError(TypeError):
    def __init__(self) -> None:
        super().__init__("JSON value must be an object or array")


class DuplicateParameterNameError(ValueError):
    def __init__(self) -> None:
        super().__init__("Duplicate parameter names are not allowed")


class ParameterModel(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str | None = Field("str", description="Parameter type as string")
    help: str | None = Field(None, description="Help text for the parameter")
    default: Any | None = Field(None, description="Default value")
    required: bool = Field(False, description="Whether parameter is required")
    show_default: bool = Field(True, description="Whether to show default in help")
    separator: str | None = Field(None, description="Separator for string lists")

    model_config = ConfigDict(
        title="Parameter Model",
        extra="allow",
        json_schema_extra={
            "example": {
                "name": "data_path",
                "type": "str",
                "help": "Path to input data file",
                "default": "/data/default.csv",
                "required": False,
                "show_default": True,
            }
        },
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        reserved_words = ["params", "with", "tag", "namespace", "obj", "tags"]
        if value in reserved_words:
            raise ParameterNameReservedError(value)
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str | None) -> str | None:
        valid_types = ["str", "int", "float", "bool", "json"]
        if value is not None and value not in valid_types:
            raise UnsupportedParameterTypeError(value)
        return value

    @field_validator("separator")
    @classmethod
    def validate_separator(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is not None and info.data.get("type") != "str":
            raise SeparatorTypeError()
        return value


class ParameterRequest(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str | None = Field("str", description="Parameter type")
    help: str | None = Field(None, description="Help text")
    default: Any | None = Field(None, description="Default value")
    required: bool | None = Field(None, description="Whether parameter is required")
    show_default: bool | None = Field(None, description="Whether to show default in help")
    separator: str | None = Field(None, description="Separator for string lists")

    model_config = ConfigDict(
        title="Parameter Request",
        extra="allow",
        json_schema_extra={
            "example": {
                "name": "worker_count",
                "type": "int",
                "help": "Number of worker processes",
                "default": 4,
                "required": False,
            }
        },
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        reserved_words = ["params", "with", "tag", "namespace", "obj", "tags"]
        if value in reserved_words:
            raise ParameterNameReservedError(value)
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str | None) -> str | None:
        valid_types = ["str", "int", "float", "bool", "json"]
        if value is not None and value not in valid_types:
            raise UnsupportedParameterTypeError(value)
        return value

    @field_validator("separator")
    @classmethod
    def validate_separator(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is not None and info.data.get("type") != "str":
            raise SeparatorTypeError()
        return value


class ParameterResponse(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    help: str | None = Field(None, description="Help text")
    default: Any | None = Field(None, description="Default value")
    required: bool = Field(False, description="Whether parameter is required")
    show_default: bool = Field(True, description="Whether to show default in help")
    is_string_type: bool = Field(False, description="Whether parameter is a string type")
    separator: str | None = Field(None, description="Separator for string lists")
    additional_properties: dict[str, Any] | None = Field(None, description="Additional properties")

    model_config = ConfigDict(
        title="Parameter Response",
        json_schema_extra={
            "example": {
                "name": "input_path",
                "type": "str",
                "help": "Path to input data",
                "default": "/data/input.csv",
                "required": True,
                "show_default": True,
                "is_string_type": True,
                "separator": None,
                "additional_properties": {"metadata": {"source": "user_input"}},
            }
        },
    )


class JSONParameterModel(BaseModel):
    value: dict[str, Any] | list[Any] = Field(..., description="JSON value as a Python object")

    model_config = ConfigDict(
        title="JSON Parameter Model",
        json_schema_extra={"example": {"value": {"workers": 4, "timeout": 30, "retry": {"count": 3, "delay": 5}}}},
    )

    @field_validator("value", mode="before")
    @classmethod
    def validate_json(cls, value: Any) -> dict[str, Any] | list[Any]:
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                if not isinstance(parsed_value, dict | list):
                    raise InvalidJSONTypeError()
                return parsed_value
            except json.JSONDecodeError as err:
                raise InvalidJSONStringError() from err
        if not isinstance(value, dict | list):
            raise InvalidJSONTypeError()
        return value


class DeployTimeFieldModel(BaseModel):
    parameter_name: str = Field(..., description="Name of the parameter")
    field: str = Field(..., description="Name of the field being computed at deploy time")
    print_representation: str | None = Field(None, description="String representation for display")

    model_config = ConfigDict(
        title="Deploy-Time Field Model",
        json_schema_extra={
            "example": {
                "parameter_name": "run_date",
                "field": "current_date",
                "print_representation": "${current_date}",
            }
        },
    )


class ParameterListResponse(BaseModel):
    parameters: list[ParameterResponse] = Field(..., description="List of parameters")
    count: int = Field(..., description="Total number of parameters")

    model_config = ConfigDict(
        title="Parameter List Response",
        json_schema_extra={
            "example": {
                "parameters": [
                    {
                        "name": "input_path",
                        "type": "str",
                        "help": "Path to input data",
                        "required": True,
                        "is_string_type": True,
                    },
                    {"name": "worker_count", "type": "int", "default": 4, "required": False, "is_string_type": False},
                ],
                "count": 2,
            }
        },
    )


class FlowParameters(BaseModel):
    flow_name: str = Field(..., description="Flow name")
    parameters: list[ParameterResponse] = Field(default_factory=list, description="Parameters defined for this flow")

    model_config = ConfigDict(
        title="Flow Parameters",
        json_schema_extra={
            "example": {
                "flow_name": "DataProcessingFlow",
                "parameters": [
                    {"name": "input_path", "type": "str", "required": True, "is_string_type": True},
                    {"name": "worker_count", "type": "int", "default": 4, "required": False, "is_string_type": False},
                ],
            }
        },
    )

    @field_validator("parameters")
    @classmethod
    def validate_parameter_names(cls, parameters: list[ParameterResponse]) -> list[ParameterResponse]:
        names = [param.name for param in parameters]
        if len(names) != len(set(names)):
            raise DuplicateParameterNameError()
        return parameters


class ParameterError(BaseModel):
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    parameter_name: str | None = Field(None, description="Name of the parameter with the error")
    field: str | None = Field(None, description="Field with the error")

    model_config = ConfigDict(
        title="Parameter Error",
        json_schema_extra={
            "example": {
                "error_code": "INVALID_TYPE",
                "message": "Unsupported parameter type: map",
                "parameter_name": "config",
                "field": "type",
            }
        },
    )
