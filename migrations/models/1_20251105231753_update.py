from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vms" ADD "password" VARCHAR(32) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vms" DROP COLUMN "password";"""


MODELS_STATE = (
    "eJztlV1r2zAUhv9K8FUL3UgcJy27SwNjG1sK3VYGpRjFUmwRWXIluR8U//fpyHZsJ7HrXC"
    "2BXcV6zyvpnIccnTcnFpgw9fEudj4N3hyOYmI+aurFwEFJUmkgaLRk1vYU2zVaKi1RoI20"
    "QkwRI2GiAkkTTQU3Kk8ZA1EExkh5WEkpp48p8bUIiY6INIH7ByNTjskLUeUyWfsrShhu5E"
    "gx3G11X78mVvvK9WdrhNuWfiBYGvPKnLzqSPCNm3INakg4kUgTOF7LFNKH7Ioiy4ryTCtL"
    "nmJtDyYrlDJdK7cng0Bw4GeyUbbAEG754I68S+9qPPWujMVmslEus7y8qvZ8oyWw+OVkNo"
    "40yh0WY8XtKfYPQrfxv0+vZNWFrxQqftV/5pgAVsDs7w6veYTkfmClf4uXSfFIecXoxWeE"
    "hzoyy6nXAedudjv/Mrs9m3rnUIswXZ+/BIsi4tpQkx9NfISxJEodQrG56zRZjiY9WI4mrS"
    "wh1GSZIKWehdzTv+0k63tOk+PY7cFx7LZyhFCWwSRZrWtvIghLFKyfkcT+TkS4os27G4rd"
    "eFtBHIWWDVQI+RdDdUYkDaJ947aIdI5cVHn+T92jGxodU5dIBSkd0Le1LafZtu6kz/tnXK"
    "2Na2PNFxBa4wCIhf00AY6Gwz4DZDhsnyAQawI0N2qS92AT4refN4v9EGtbtkD+5qbAe0wD"
    "fTFgVOmH48TaQRGqhqRjpR5ZHd7Zj9mfba7z7zfXloJQOpT2FHvA9b8eL9lfRFxiPw=="
)
