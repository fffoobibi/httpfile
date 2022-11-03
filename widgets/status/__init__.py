module_name = 'widgets.status'
status_controls = {}

__all__ = ('load_status_control_widgets',)


def register(name: str, index: int = 0, icon: str = None):
    def get_register(self, key, dft=None):
        return {'name': name, 'index': index, 'icon': icon}.get(key, dft)

    def wrapper(clz):
        clz.get_register = get_register
        status_controls[clz] = {'name': name, 'index': index, 'icon': icon}
        return clz

    return wrapper


def load_status_control_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('status_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', module_name)
    return status_controls
