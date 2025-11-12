from tortoise import fields
from tortoise.models import Model


class Vm(Model):
    id = fields.IntField(pk=True)
    vm_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=64, unique=True)
    ip_address = fields.CharField(max_length=15, unique=True)
    password = fields.CharField(max_length=32)
    domain = fields.CharField(max_length=64, null=True)

    class Meta:
        table = "vms"

    def __str__(self):
        return f"{self.name} ({self.ip_address or 'no-ip'})"
