from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Chunk:
    id: str
    doc_name: str
    section: str
    text: str
    level: str
    parent_id: Optional[str] = None