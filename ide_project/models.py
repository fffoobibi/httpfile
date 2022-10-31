from pydantic import BaseModel

class RunData(BaseModel):
    current_dir: str=None
