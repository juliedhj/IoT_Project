from coapthon.client.helperclient import HelperClient

client = HelperClient(server=('coap://130.136.2.70/test', 5683))
response = client.get('other/block')
client.stop()