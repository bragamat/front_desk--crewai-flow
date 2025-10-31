

from litellm import BaseModel
from pydantic import Field


class TranslationCrewOutput(BaseModel):
    output: str = Field(..., description="Translated text output")
    language: str = Field(..., description="Detected language of the input text")
    formality_level: str = Field(..., description="Formality level of the translation")
    cultural_notes: str = Field(..., description="Cultural notes related to the translation")

