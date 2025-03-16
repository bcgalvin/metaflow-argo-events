import time
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class ArgoEventSchema(BaseModel):
    name: str = Field(
        ..., description="Event name that targets will listen for", min_length=1, examples=["data_processed"]
    )
    url: AnyHttpUrl | None = Field(
        default=None, description="Webhook endpoint URL", examples=["https://events.example.com/webhook"]
    )
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    access_token: str | None = Field(
        default=None,
        description="Authentication token for Bearer auth",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    model_config = ConfigDict(
        title="Argo Event Schema",
        json_schema_extra={
            "example": {
                "name": "data_processed",
                "url": "https://events.example.com/webhook",
                "payload": {"status": "success", "count": "42"},
            }
        },
    )


class PayloadItem(BaseModel):
    key: str = Field(..., description="Key for the payload entry", examples=["status"])
    value: Any = Field(
        ..., description="Value for the payload entry (will be converted to string)", examples=["success", 42, True]
    )

    @field_validator("value")
    @classmethod
    def convert_to_string(cls, v: Any) -> str:
        return str(v)


class PublishOptions(BaseModel):
    force: bool = Field(default=True, description="Whether to publish regardless of environment")
    ignore_errors: bool = Field(default=True, description="Whether to suppress errors")
    additional_payload: dict[str, Any] | None = Field(default=None, description="Additional payload data to include")

    model_config = ConfigDict(
        title="Publish Options",
        json_schema_extra={
            "example": {"force": True, "ignore_errors": True, "additional_payload": {"status": "success"}}
        },
    )


class PublishResult(BaseModel):
    success: bool = Field(..., description="Whether publication succeeded", examples=[True])
    event_id: str | None = Field(
        default=None,
        description="Unique event identifier if successful",
        examples=["f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f"],
    )
    error_message: str | None = Field(
        default=None, description="Error message if publication failed", examples=["Unable to connect to webhook URL"]
    )
    timestamp: int = Field(
        default_factory=lambda: int(time.time()), description="When the result was generated", examples=[1684159845]
    )

    model_config = ConfigDict(
        title="Publish Result",
        json_schema_extra={
            "examples": [
                {"success": True, "event_id": "f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f", "timestamp": 1684159845},
                {"success": False, "error_message": "Failed to connect to webhook URL", "timestamp": 1684159845},
            ]
        },
    )


class ArgoEventPayload(BaseModel):
    name: str = Field(..., description="Event name", examples=["data_processed"])
    id: str = Field(..., description="Unique event identifier", examples=["f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f"])
    timestamp: int = Field(..., description="Unix timestamp when event was created", examples=[1684159845])
    utc_date: str = Field(..., description="UTC date in YYYYMMDD format", examples=["20230515"])
    generated_by_metaflow: bool = Field(default=True, description="Flag indicating Metaflow generation")

    # allow additional properties for dynamic fields
    model_config = ConfigDict(
        extra="allow",
        title="Argo Event Payload",
        json_schema_extra={
            "example": {
                "name": "data_processed",
                "id": "f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f",
                "timestamp": 1684159845,
                "utc_date": "20230515",
                "generated_by_metaflow": True,
                "status": "success",
                "count": "42",
            }
        },
    )


class CreateArgoEventInput(BaseModel):
    name: str = Field(
        ..., description="Name of the event to create", min_length=1, examples=["data_processed", "model_trained"]
    )
    url: str | None = Field(
        default=None, description="Webhook endpoint URL", examples=["https://events.example.com/webhook"]
    )
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Initial event payload data", examples=[{"status": "success", "count": 42}]
    )
    access_token: str | None = Field(
        default=None,
        description="Authentication token for Bearer auth",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    force: bool = Field(default=True, description="Whether to publish regardless of environment")
    ignore_errors: bool = Field(default=True, description="Whether to suppress errors")

    model_config = ConfigDict(
        title="Create Argo Event Input",
        json_schema_extra={
            "example": {
                "name": "data_processed",
                "payload": {"status": "success", "count": 42},
                "force": True,
                "ignore_errors": True,
            }
        },
    )

    @field_validator("payload", mode="before")
    @classmethod
    def validate_payload_values(cls, v: dict[str, object] | None) -> dict[str, str]:
        if isinstance(v, dict):
            return {k: str(val) for k, val in v.items()}
        return v


class ArgoEventOutput(BaseModel):
    event_id: str = Field(
        ..., description="Unique identifier of the published event", examples=["f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f"]
    )
    name: str = Field(..., description="Name of the published event", examples=["data_processed"])
    timestamp: int = Field(..., description="Unix timestamp when event was published", examples=[1684159845])
    status: str = Field(default="published", description="Publication status", examples=["published"])
    payload: dict[str, Any] | None = Field(default=None, description="Event payload data")

    model_config = ConfigDict(
        title="Argo Event Output",
        json_schema_extra={
            "example": {
                "event_id": "f8d7e9c6-5b4a-3c2d-1e0f-9a8b7c6d5e4f",
                "name": "data_processed",
                "timestamp": 1684159845,
                "status": "published",
                "payload": {"status": "success", "count": "42"},
            }
        },
    )
