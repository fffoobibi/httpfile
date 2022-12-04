# import asyncio
#
# from aiohttp_json_rpc import JsonRpcClient
#
# {
#     "jsonrpc": "2.0",
#     "id": 1,
#     "method": "textDocument/definition",
#     "params": {
#         "textDocument": {
#             "uri": "file:///C:/Users/fqk12/Desktop/httpfile/2.py"
#         },
#         "position": {
#             "line": 3,
#             "character": 1
#         }
#     }
# }
#
# import pyls
#
# params = {
#     "textDocument": {
#         "uri": "file:///C:/Users/fqk12/Desktop/httpfile/2.py"
#     },
#     "position": {
#         "line": 3,
#         "character": 1
#     }}
#
#
# async def definition(request):
#     print(request.params, )
#
#
# async def ping_json_rpc():
#     """Connect to ws://localhost:8080/, call ping() and disconnect."""
#     rpc_client = JsonRpcClient()
#     rpc_client.add_methods(['textDocument', definition])
#     try:
#         await rpc_client.connect('localhost', 2087)
#         call_result = await rpc_client.call(definition, params=params)
#         print(call_result)  # prints 'pong' (if that's return val of ping)
#     finally:
#         await rpc_client.disconnect()
#
#
# if __name__ == '__main__':
#     asyncio.run(ping_json_rpc())
#
#     # import requests
#     #
#     # requests.post('http://127.0.0.1:2087', data={
#     #     'jsonrpc': '2.0',
#     #     'id': '1',
#     #     'method': 'asdfsdfsf'
#     # })

import pyls
import pyls_jsonrpc

# import socket
# sock = socket.socket()

import requests

requests.post('http://127.0.0.1:2087', data={
    'jsonrpc': '2.0',
    'id': '1',
    'method': 'asdfsdfsf',
    'params':
        {

        }
})
