from pydantic import BaseModel


class ReportInfo(BaseModel):
    name: str
    filename: str
