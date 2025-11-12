from pydantic import BaseModel


class CreateVmShema(BaseModel):
    template_id: int
    memory: int
    cores: int
    disk_gb: int
    name: str
    password: str
