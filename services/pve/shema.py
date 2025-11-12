from enum import StrEnum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OSInfo(BaseModel):
    name: Optional[str]
    version: Optional[str]
    kernel: Optional[str]


# =============================================================
# === Agent ===
# =============================================================


class AgentInterfaceAddress(BaseModel):
    ip_address: str = Field(..., alias="ip-address")
    prefix: Optional[int] = None

class AgentInterface(BaseModel):
    name: str
    hardware_address: Optional[str] = Field(None, alias="hardware-address")
    ip_addresses: Optional[List[AgentInterfaceAddress]] = Field(None, alias="ip-addresses")

class AgentOSInfo(BaseModel):
    name: Optional[str]
    version: Optional[str]
    kernel_release: Optional[str] = Field(None, alias="kernel-release")


# class AgentInfo(BaseModel):
#     interfaces: Optional[List[AgentInterface]] = None
#     osinfo: Optional[AgentOSInfo] = None
#
# # =============================================================
# # === Status / Config DTO ===
# # =============================================================
#
# class VMStatusInfo(BaseModel):
#     status: Optional[str]
#     uptime: Optional[int]
#     cpu: Optional[float]
#     cpus: Optional[int]
#     mem: Optional[int]
#     maxmem: Optional[int]
#     disk: Optional[int]
#     maxdisk: Optional[int]
#     name: Optional[str]
#     pid: Optional[int]
#     qmpstatus: Optional[str]
#     freemem: Optional[int] = None
#     netin: Optional[int] = None
#     netout: Optional[int] = None
#     diskwrite: Optional[int] = None
#     diskread: Optional[int] = None
#
#
# class VMConfigInfo(BaseModel):
#     name: Optional[str]
#     cores: Optional[int]
#     memory: Optional[int]
#     bootdisk: Optional[str]
#     net0: Optional[str]
#     ipconfig0: Optional[str]
#     cicustom: Optional[str]
#     ciuser: Optional[str]
#     cipassword: Optional[str]
#     nameserver: Optional[str]
#     sockets: Optional[int]
#     numa: Optional[int]
#     machine: Optional[str]
#     cpu: Optional[str]
#     scsihw: Optional[str]
#     ide2: Optional[str]
#     scsi0: Optional[str]
#     vmgenid: Optional[str]
#     vga: Optional[str]
#     digest: Optional[str]
#     smbios1: Optional[str]
#     serial0: Optional[str]
#
#
# # =============================================================
# # === Summary (high-level aggregated view) ===
# # =============================================================
#
# class VMSummary(BaseModel):
#     vmid: int
#     name: Optional[str]
#     status: Optional[str]
#     uptime_sec: Optional[int]
#     cpu_usage: Optional[float] = Field(None, description="CPU usage in %")
#     cores: Optional[int]
#     max_cpu: Optional[int]
#     ram_usage_mb: Optional[float]
#     ram_total_mb: Optional[float]
#     disk_usage_gb: Optional[float]
#     disk_total_gb: Optional[float]
#     bootdisk: Optional[str]
#     net: Optional[str]
#     ip_addresses: List[str] = []
#     os: Optional[AgentOSInfo]
#
#     @property
#     def cpu_usage_percent(self) -> str:
#         return f"{self.cpu_usage:.2f}%" if self.cpu_usage is not None else "N/A"
#
#     @property
#     def ram_usage_str(self) -> str:
#         if self.ram_usage_mb and self.ram_total_mb:
#             return f"{self.ram_usage_mb:.0f}/{self.ram_total_mb:.0f} MB"
#         return "N/A"
#
#
# # =============================================================
# # === Root schema ===
# # =============================================================
#
# class VmFullInfo(BaseModel):
#     vmid: int
#     summary: VMSummary
#     status: VMStatusInfo
#     config: VMConfigInfo
#     agent: AgentInfo | None


class VmStatus(StrEnum):
    running = "running"
    stopped = "stopped"


class VmInfo(BaseModel):
    vmid: int
    name: str
    status: VmStatus
    cpus: int
    cpu: float
    mem: int
    maxmem: int
    disk: int
    maxdisk: int
    diskwrite: int
    diskread: int
    netin: int
    netout: int
    uptime: int

    serial: int | None = None
    template: int | None = None
    pid: int | None = None

    ip_addresses: list[str] = []
    os_name: str | None = None
    os_type: str | None = None

    # derived / удобные поля
    @property
    def cpu_usage_percent(self) -> str:
        return f"{self.cpu * 100:.1f}%" if self.cpu is not None else "N/A"

    @property
    def ram_usage_mb(self) -> float:
        return round(self.mem / 1024 / 1024, 2)

    @property
    def ram_total_mb(self) -> float:
        return round(self.maxmem / 1024 / 1024, 2)

    @property
    def disk_usage_gb(self) -> float:
        return round(self.disk / 1024 / 1024 / 1024, 2)

    @property
    def disk_total_gb(self) -> float:
        return round(self.maxdisk / 1024 / 1024 / 1024, 2)

    @property
    def ram_usage_str(self) -> str:
        if self.mem is not None and self.maxmem is not None:
            return f"{self.ram_usage_mb:.0f}/{self.ram_total_mb:.0f} MB"
        return "N/A"

    @property
    def disk_usage_str(self) -> str:
        if self.disk is not None and self.maxdisk is not None:
            return f"{self.disk_usage_gb:.1f}/{self.disk_total_gb:.1f} GB"
        return "N/A"