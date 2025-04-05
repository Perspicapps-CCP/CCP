# File to validate the data that is being sent and received to the API

from pydantic import BaseModel


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"
