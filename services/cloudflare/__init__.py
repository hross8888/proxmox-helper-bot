from core.settings import CF_TOKEN, DOMAIN
from services.cloudflare.api import CloudflareAPI

cloudflare = CloudflareAPI(api_token=CF_TOKEN, domain=DOMAIN)