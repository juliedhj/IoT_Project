#IP CoAP server: coap://130.136.2.70, port: 5683
import logging
import asyncio

import aiocoap 

server = 'coap://130.136.2.70:5683/test'
logging.basicConfig(level=logging.INFO)

async def main():
    protocol = await aiocoap.Context.create_client_context()

    request = aiocoap.Message(code=aiocoap.GET, uri=server)

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    asyncio.run(main())