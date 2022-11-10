from dataclasses import dataclass


@dataclass
class Request:
    url: str
    method: str
    headers: dict
    status: int = -1
