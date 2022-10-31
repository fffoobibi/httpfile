from pathlib import Path

from flask import Flask, Response
from multiprocessing import Process


def _web_task(static_folder: str, port=6666):
    app = Flask(__name__, static_folder=static_folder, static_url_path='/')
    replace_name = Path(static_folder).__str__()

    def _process(current: Path):
        dirs = list(current.iterdir())
        ret_ = []
        dirs.sort(key=lambda e: 0 if e.is_dir() else 1)
        for d in dirs:
            if d.is_file():
                ret_.append(d.__str__().replace(replace_name, ''))
            else:
                ret_.append(_process(d))
        return ret_

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
