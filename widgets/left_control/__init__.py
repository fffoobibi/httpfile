module_name = 'widgets.left_control'
left_controls = {}


def register(name: str, index: int = 0):
    def wrapper(clz):
        left_controls[clz] = {'name': name, 'index': index}
        return clz

    return wrapper


def load_left_control_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('control_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', module_name)
    return left_controls
