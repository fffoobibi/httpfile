http_hooks = """

def before_request(request):
    pass


def after_request(response):
    pass

"""

_lsp_hooks = {}


def run_lsp_hook(serve_name: str, editor):
    h = _lsp_hooks.get(serve_name)
    if h:
        h(serve_name, editor)


def register_lsp_hook(serve_name: str, func):
    _lsp_hooks.setdefault(serve_name, func)
