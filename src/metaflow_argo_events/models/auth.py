from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BearerTokenMissingError(ValueError):
    """Error raised when bearer token is missing."""

    def __init__(self) -> None:
        super().__init__("bearer_token must be provided when method is 'bearer'")


class ServiceHeadersMissingError(ValueError):
    """Error raised when service headers are missing."""

    def __init__(self) -> None:
        super().__init__("service_headers must be provided when method is 'service'")


class BearerAuth(BaseModel):
    token: str = Field(
        ..., description="Bearer token for authentication", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    model_config = ConfigDict(title="Bearer Authentication")


class ServiceAuth(BaseModel):
    headers: dict[str, str] = Field(
        ..., description="Headers for service authentication", examples=[{"X-API-Key": "api-key-value"}]
    )

    model_config = ConfigDict(title="Service Authentication")


class AuthConfig(BaseModel):
    method: Literal["none", "bearer", "service"] = Field(default="none", description="Authentication method to use")
    bearer_token: str | None = Field(
        default=None,
        description="Bearer token for authentication",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    service_headers: dict[str, str] | None = Field(
        default=None, description="Headers for service authentication", examples=[{"X-API-Key": "api-key-value"}]
    )

    model_config = ConfigDict(title="Authentication Configuration")

    @model_validator(mode="after")
    def validate_auth_config(self) -> "AuthConfig":
        if self.method == "bearer" and not self.bearer_token:
            raise BearerTokenMissingError()
        if self.method == "service" and not self.service_headers:
            raise ServiceHeadersMissingError()
        return self
