import aiohttp
if not hasattr(aiohttp, "ClientConnectorDNSError"):
    aiohttp.ClientConnectorDNSError = aiohttp.ClientConnectorError