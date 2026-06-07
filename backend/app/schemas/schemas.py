from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class PromptItem(BaseModel):
    id: str
    prompt: str
    failure_category: str
    detection_method: str
    rule: Optional[str] = None
    expected_output: Optional[str] = None
    judge_instruction: Optional[str] = None

class TestCollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prompts: List[PromptItem]

class TestCollectionOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    # using List[Dict] here instead of List[PromptItem] as SQLAlchemy returns the JSON blog as raw dicts
    prompts: List[Dict]
    created_at: datetime
    class Config:
        from_attributes = True

class RunCreate(BaseModel):
    collection_id: str
    model: str = "claude-sonnet-4-20250514"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class RunOut(BaseModel):
    id: str
    collection_id: str
    model: str
    temperature: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    class Config:
        from_attributes = True

class ResultOut(BaseModel):
    id: str
    run_id: str
    prompt_id: str
    prompt_text: str
    model_output: str
    failure_category: Optional[str]
    # 0 = pass and 1 = fail
    is_failure: int
    judge_reasoning: Optional[str]
    judge_confidence: Optional[float]
    # 0 = normal confidence and 1 = low confidence flag
    low_confidence: int
    detection_method: str
    created_at: datetime
    class Config:
        from_attributes = True

class RunSummary(BaseModel):
    run: RunOut
    total: int
    failures: int
    failure_rate: float
    low_confidence_count: int
    by_category: Dict[str, int]
    results: List[ResultOut]