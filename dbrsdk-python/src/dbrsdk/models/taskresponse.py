"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from dbrsdk.types import BaseModel
from typing_extensions import TypedDict


class TaskResponseTypedDict(TypedDict):
    id: int
    title: str
    completed: bool


class TaskResponse(BaseModel):
    id: int

    title: str

    completed: bool
