import json
from pathlib import Path
import socket
import pyls
import json_lsp
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

port = 3999
server_ip_port = ('127.0.0.1', port)  # 不写本机ip会拿1个可用的ip来用, 2087

# sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sk.connect(server_ip_port)

d2 = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "textDocument/refer",
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
        }}
d2 = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params":
        {
            "processId": 1,
            "rootUri": "file:///D:/work/httpfile/.env.json",
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
d2 = json.dumps(d2, ensure_ascii=False)
d1 = 'Content-Length: %s\r\n\r\n' % len(d2.encode())
print(d1)
print(d2)
# sk.send(d1.encode())
# sk.send(d2.encode())
#
# txt = ''
# while True:
#     server_reply = sk.recv(1024).decode()  # 接受服务端的返回结果,反解成字符串
#     txt += server_reply
#     if not server_reply:
#         break
#     print('res ', repr(txt))
#
# sk.close()

from jsonrpcx import acall
import pyls_jsonrpc
import asyncio

params = {
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

async def main():
    d2 = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params":
            {
                "processId": 1,
                "rootUri": "file:///D:/work/httpfile/.env.json",
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
    # from jsonrpcx import acall
    # result1 = await acall("http://127.0.0.1:2087", method="initialize", params=d2['params'])
    # print(result1)
    import httpx
    # length = len(json.dumps(d2, ensure_ascii=False).encode())
    # t= None
    async with httpx.AsyncClient() as client:
        client: httpx.AsyncClient
        resp = await client.post('https://127.0.0.1:3999', json=d2, )

        print(resp.text)


if __name__ == "__main__":
    asyncio.run(main())
