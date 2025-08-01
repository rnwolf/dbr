"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from dbrsdk.types import BaseModel
from dbrsdk.utils import FieldMetadata, PathParamMetadata
from typing_extensions import Annotated, TypedDict


class DeleteOrganizationAPIV1OrganizationsOrgIDDeleteRequestTypedDict(TypedDict):
    org_id: str


class DeleteOrganizationAPIV1OrganizationsOrgIDDeleteRequest(BaseModel):
    org_id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
