import logging
import asyncio

import aiocoap 

logging.basicConfig(level=logging.INFO)

true = True
while (True):
    async def main():
        """Perform a single PUT request to localhost on the default port, URI
        "/other/block". The request is sent 2 seconds after initialization.

        The payload is bigger than 1kB, and thus sent as several blocks."""

        context = await aiocoap.Context.create_client_context()

        await asyncio.sleep(2)

        payload = b"Test message.\n" 
        request = aiocoap.Message(code=aiocoap.POST, payload=payload, uri="coap://130.136.2.70:5683/test")

        response = await context.request(request).response

        print('Result POST: %s\n%r'%(response.code, response.payload))

    if __name__ == "__main__":
        asyncio.run(main())