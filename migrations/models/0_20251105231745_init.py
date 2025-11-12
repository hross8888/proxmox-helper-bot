from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "vms" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "vm_id" INT NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "ip_address" VARCHAR(15) NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztlV1r2zAUhv9K8FUL3Ug8Jy27SwNjG1sK3VYGpRjFUmwRfbiS3LUU//fpyHZk56vJ1R"
    "LYVaz3vJLOecjReQ24xITp93c8+Nh7DQTixH601ItegPLcayAYNGPO9sTdGs20USgxVpoj"
    "pomVMNGJormhUlhVFIyBKBNrpCL1UiHoY0FiI1NiMqJs4P7BylRg8kx0s8wX8ZwShjs5Ug"
    "x3Oz02L7nTvgjzyRnhtlmcSFZw4c35i8mkWLqpMKCmRBCFDIHjjSogfciuLrKpqMrUW6oU"
    "W3swmaOCmVa5ezJIpAB+NhvtCkzhlnfhILqMrj6MoitrcZkslcuyKs/XXm10BKY/g9LFkU"
    "GVw2H03J54fBC6pf9teg2rXfgawfPz/5ljAuiBud81XpMMqc3AGv8KL5vikfLi6DlmRKQm"
    "s8tRtAPO3fh28nl8ezaKzqEWabu+egmmdSR0oS4/mscIY0W0PoRid9dpshwM92A5GG5lCa"
    "GyhBdwvmj1MggzlCz+IIXjtYgM5TbveoiHfFVBAqWODVQI+dfDYEwUTbJNY6KO7BwVyHv+"
    "T4uje+x2TAuiNKR0QOe2tpxm24bDffrWurY2rot1X0FojQMg1vbTBDjo9/d5+Pr97S8fxL"
    "oA7Y2GVD3Yhfj1x810M8TWlhWQv4Qt8B7TxFz0GNXm4Tix7qAIVUPSXOtH1oZ39n38e5Xr"
    "5NvNtaMgtUmVO8UdcP2vx0v5F0Lu+TE="
)
