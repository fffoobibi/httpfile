tab_codes = {}


def register(file_types: list):
    def wrapper(clz):
        tab_codes[clz] = [f'{f} File' for f in file_types]
        return clz

    return wrapper


def load_tab_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('tab_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', 'widgets.tabs')
    return tab_codes
