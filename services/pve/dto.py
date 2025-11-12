from typing import Any, Dict, Optional
from pydantic import BaseModel


class PveResponse(BaseModel):
    data: Any


class PveVMStatus(BaseModel):
    status: str
    uptime: Optional[int]
    cpu: Optional[float]
    cpus: Optional[int]
    mem: Optional[int]
    maxmem: Optional[int]
    disk: Optional[int]
    maxdisk: Optional[int]


class PveVMConfig(BaseModel):
    name: Optional[str]
    cores: Optional[int]
    memory: Optional[int]
    bootdisk: Optional[str]
    net0: Optional[str]


class PveCloneDTO(BaseModel):
    newid: int
    name: str
    full: int