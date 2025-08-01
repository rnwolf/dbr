"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from .membershipcreate import MembershipCreate, MembershipCreateTypedDict
from dbrsdk.types import BaseModel
from dbrsdk.utils import FieldMetadata, PathParamMetadata, RequestMetadata
from typing_extensions import Annotated, TypedDict


class CreateMembershipAPIV1OrganizationsOrgIDMembershipsPostRequestTypedDict(TypedDict):
    org_id: str
    membership_create: MembershipCreateTypedDict


class CreateMembershipAPIV1OrganizationsOrgIDMembershipsPostRequest(BaseModel):
    org_id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]

    membership_create: Annotated[
        MembershipCreate,
        FieldMetadata(request=RequestMetadata(media_type="application/json")),
    ]
