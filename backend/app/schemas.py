from pydantic import BaseModel


class UserFeatures(BaseModel):
    device_connections: int
    emails_sent: int
    files_accessed: int
    websites_visited: int
    logon_count: int
    O: int
    C: int
    E: int
    A: int
    N: int