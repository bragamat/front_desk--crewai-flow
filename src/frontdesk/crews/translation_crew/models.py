

from typing import Optional
from pydantic import Field, BaseModel

class TranslationCrewOutput(BaseModel):
    output: str = Field(..., description="Translated text output")
    original: str = Field(..., description="Original input text")
    language: Optional[str] = Field(..., description="Detected language of the input text")
    formality_level: Optional[str] = Field(..., description="Formality level of the translation")
    cultural_notes: Optional[str] = Field(..., description="Cultural notes related to the translation")

