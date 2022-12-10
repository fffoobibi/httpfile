a = {'source': 'pyflakes', 'range': {'start': {'line': 5, 'character': 7}, 'end': {'line': 5, 'character': 28}},
     'message': 'invalid syntax', 'severity': 1}

from lsprotocol.converters import get_converter
from lsprotocol.types import TextDocumentDiagnosticResponse, Diagnostic, Range

# print(a)
c = get_converter().structure(a, Diagnostic)

print(c)
