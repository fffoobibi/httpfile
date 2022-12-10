_hooks = {}


def run_hook(hook_type: str):
    h = _hooks.get(hook_type)
    if h:
        h()
