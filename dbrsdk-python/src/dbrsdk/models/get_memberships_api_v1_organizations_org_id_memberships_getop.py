"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from dbrsdk.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
from dbrsdk.utils import FieldMetadata, PathParamMetadata, QueryParamMetadata
from pydantic import model_serializer
from typing_extensions import Annotated, NotRequired, TypedDict


class GetMembershipsAPIV1OrganizationsOrgIDMembershipsGetRequestTypedDict(TypedDict):
    org_id: str
    role_id: NotRequired[Nullable[str]]
    r"""Filter by role ID"""
    status: NotRequired[Nullable[str]]
    r"""Filter by invitation status"""


class GetMembershipsAPIV1OrganizationsOrgIDMembershipsGetRequest(BaseModel):
    org_id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]

    role_id: Annotated[
        OptionalNullable[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = UNSET
    r"""Filter by role ID"""

    status: Annotated[
        OptionalNullable[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = UNSET
    r"""Filter by invitation status"""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["role_id", "status"]
        nullable_fields = ["role_id", "status"]
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
