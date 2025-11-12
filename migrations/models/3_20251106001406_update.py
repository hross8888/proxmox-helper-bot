from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vms" ADD "domain" VARCHAR(64);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vms" DROP COLUMN "domain";"""


MODELS_STATE = (
    "eJztlmtr2zAUhv9KyKcOupE4l5Z9SwNjG1sK3VYGpRjFUhwRXVxJ7oWS/14d2YnsJM7s0d"
    "EE9in2e95jnfMQ6ei5zSUmTH+45u2Pree2QJzYh4J62mqjJPEaCAZNmbPdc/eOptooFBkr"
    "zRDTxEqY6EjRxFAprCpSxkCUkTVSEXspFfQuJaGRMTFzomzg5tbKVGDySPTqNVmEM0oYLt"
    "VIMazt9NA8JU77IswnZ4TVpmEkWcqFNydPZi7F2k2FATUmgihkCHzeqBTKh+ryJlcdZZV6"
    "S1ZiIQeTGUqZKbRbk0EkBfCz1WjXYAyrvA+6/bP+eW/YP7cWV8laOVtm7fnes0RHYPKzvX"
    "RxZFDmcBg9t3seNkK39v+Z3orV8ePzuNzvFq3xHKnduFb+DVq2xIOkxdFjyIiIzdy+Dvt7"
    "0FyPrsafR1cnw/476ETaHZ+dApM8ErhQmR5NQoSxIlo3YVjOOkaS3UENkt1BJUkIlUkmSO"
    "sHqXbs3GqOxZzXobgSPEZ/4v8Ljr2gBsdeUMkRQmWOWHK7VhOKPuOvGOb/szdD+DqbGsbw"
    "bFEYKCBMUbR4QAqHWxEZyCrvdogHfFNBAsWODXQI9ec3khFRNJrvuqvkkb33FeQ9/68sBz"
    "dz91xZiNJQUoNNW0g5zpMvGNQZIdZVuXFdrHz4wdZoADG3HyfAbqdTZwZ3OtVDGGJlgHZF"
    "Q7I9WIb49cflZDfEQsoGyF/CNniDaWROW4xqc3uYWPdQhK6haK71HSvCO/k++r3Jdfzt8s"
    "JRkNrEyn3FfeDircfL8gUJBMdK"
)
