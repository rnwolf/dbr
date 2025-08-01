"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from dbrsdk.types import BaseModel, Nullable, UNSET_SENTINEL
from pydantic import model_serializer
from typing_extensions import TypedDict


class OrganizationResponseTypedDict(TypedDict):
    r"""Schema for organization response"""

    id: str
    name: str
    description: Nullable[str]
    status: str
    contact_email: str
    country: str
    subscription_level: str
    default_board_id: Nullable[str]
    created_date: str
    updated_date: str


class OrganizationResponse(BaseModel):
    r"""Schema for organization response"""

    id: str

    name: str

    description: Nullable[str]

    status: str

    contact_email: str

    country: str

    subscription_level: str

    default_board_id: Nullable[str]

    created_date: str

    updated_date: str

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = []
        nullable_fields = ["description", "default_board_id"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m
