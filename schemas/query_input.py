from pydantic import BaseModel
from typing import List, Dict

class QueryInput(BaseModel):
    question: str
    history: List[Dict[str,str]]
    time: str
    alreadyPrompted: bool