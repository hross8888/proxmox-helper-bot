from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_vms_vm_id_e3e273" ON "vms" ("vm_id");
        CREATE UNIQUE INDEX "uid_vms_ip_addr_ced159" ON "vms" ("ip_address");
        CREATE UNIQUE INDEX "uid_vms_name_3c80fc" ON "vms" ("name");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_vms_name_3c80fc";
        DROP INDEX IF EXISTS "uid_vms_ip_addr_ced159";
        DROP INDEX IF EXISTS "uid_vms_vm_id_e3e273";"""


MODELS_STATE = (
    "eJztlW9r2zAQxr9K8KsOupE4Tlr2Lg2MbWwpdFsZlGIUS7FFZMmV5P6h5LtPJ9uRncSZAx"
    "tLYK8SP/ecdPeD0716qcCEqXe3qfe+9+pxlBLzp6ae9zyUZU4DQaM5s7bH1H6judISRdpI"
    "C8QUMRImKpI001Rwo/KcMRBFZIyUx07KOX3ISahFTHRCpAnc3RuZckyeiao+s2W4oIThRo"
    "0Uw91WD/VLZrVPXH+wRrhtHkaC5Sl35uxFJ4Kv3ZRrUGPCiUSawPFa5lA+VFc2WXVUVOos"
    "RYm1HEwWKGe61m5HBpHgwM9Uo2yDMdzy1h8EF8HlcBxcGoutZK1crIr2XO9FoiUw++6tbB"
    "xpVDgsRsftMQ0PQrf2/55exer08Tlc9neL1jRBcjeuyr9By5R4lLRS9BwywmOdmM9xsAfN"
    "7eRm+nFyczYO3kAnwkx88QrMyohvQ016NAsRxpIodQjDZtYpkhyMOpAcjFpJQqhJMkNKPQ"
    "m5Y3LbOdZz/gzFSnAY3Yv/NzgO/Q4ch34rRwitVrBDFsvaawjCHEXLJyRxuBURvmjzbodS"
    "P91UEEexZQMdQv3lOp0QSaNk16ItI3uXLXKe//v26BbGnn1LpIKSDpjbWsppjq0/6vL+GV"
    "fr4NpY8wWE0TgAYmk/TYCDfr/LAun32zcIxJoAzY2aFDPYhPj52/VsN8RaygbIH9w0eIdp"
    "pM97jCp9f5xY91CErqHoVKkHVod39nXyc5Pr9Mv1laUglI6lPcUecPWv18vqF4QkYH0="
)
