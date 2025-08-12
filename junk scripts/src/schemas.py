from pydantic import BaseModel, Field, AwareDatetime
from typing import List, Optional

class ImportItem(BaseModel):
    slug: str
    title: str
    url: str
    difficulty: Optional[str] = None
    lcTags: List[str] = Field(default_factory=list)
    lang: Optional[str] = None
    submittedAt: AwareDatetime

class ImportBatch(BaseModel):
    userId: str
    items: List[ImportItem]
