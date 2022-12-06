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
import json
from pathlib import Path
import requests

# import pyls
#
# file = Path(r'D:/work/httpfile/scrap.py').read_bytes()
# headers = {'Content-Length': str(len(file))}
# resp = requests.post('http://127.0.0.1:2087',
#                      headers=headers,
#                      data={
#                          'jsonrpc': '2.0',
#                          'id': '1',
#                          'method': 'initialize',
#                          'params':
#                              {
#                                  'processId': 1,
#                                  'rootUri': 'file:///D:/work/httpfile/scrap.py',
#                                  'capabilities': {
#                                      'textDocument': {
#                                          'completion': {},
#                                          'hover': {},
#                                          'definition': {},
#                                          'references': {},
#                                          'documentHighlight': {},
#                                          'signatureHelp': {}
#                                      }
#                                  }
#                              }
#                      })
# print('---------------')
# print(resp.text)
# print(resp.status_code)
data = {
    'jsonrpc': '2.0',
    'id': '1',
    'method': 'initialize',
    'params':
        {
            'processId': 1,
            'rootUri': 'file:///D:/work/httpfile/scrap.py',
            'capabilities': {
                'textDocument': {
                    'completion': {},
                    'hover': {},
                    'definition': {},
                    'references': {},
                    'documentHighlight': {},
                    'signatureHelp': {}
                }
            }
        }
}
import socket

file = Path(r'D:/work/httpfile/scrap.py').read_bytes()
# headers = {'Content-Length': str(len(file))}
data = r'''Content-Length: %s
\r\n
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params":
        {
            "processId": 1,
            "rootUri": "file:///D:/work/httpfile/scrap.py",
            "capabilities": {
                "textDocument": {
                    "completion": {},
                    "hover": {},
                    "definition": {},
                    "references": {},
                    "documentHighlight": {},
                    "signatureHelp": {}
                }
            }
        }
}
''' % len(file)

print(repr(data))
server_ip_port = ('127.0.0.1', 2087)  # 不写本机ip会拿1个可用的ip来用

sk = socket.socket()
sk.connect(server_ip_port)
sk.sendall(data.encode('utf-8'))  # 向服务端发送数据，以字节流的方式发送

txt = ''
while True:
    server_reply = sk.recv(1024).decode()  # 接受服务端的返回结果,反解成字符串
    print('get ---', server_reply)
    txt += server_reply
    if not server_reply:
        break

sk.close()
print('res ', txt)
