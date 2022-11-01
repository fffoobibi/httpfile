from pathlib import Path

from flask import Flask
from multiprocessing import Process, Queue


def _web_task(static_folder: str, port=9527):
    app = Flask(__name__, static_folder=static_folder, static_url_path='/')
    replace_name = Path(static_folder).__str__()
    print('replace_name ', replace_name)

    def _process(current: Path) -> dict:
        dirs = list(current.iterdir())
        root = {}
        top_path = current.__str__().replace(replace_name, '')
        dirs.sort(key=lambda e: 0 if e.is_dir() else 1)
        for d in dirs:
            if d.is_file():
                v = root.setdefault(top_path, [])
                v.append(d.__str__().replace(replace_name, ''))
            else:
                v = root.setdefault(top_path, [])
                v.append(_process(d))
        if not dirs:
            root.setdefault(top_path, [])

        return root

    @app.get('/')
    def index():
        current = Path(static_folder)
        ret = _process(current)
        return dict(code=0, data=ret)

    app.run(host='0.0.0.0', port=port, debug=False)


def web_server_run(static_folder: str):
    print('run serve folder at: ', static_folder)
    process = Process(target=_web_task, args=(static_folder,))
    process.start()
    return process
