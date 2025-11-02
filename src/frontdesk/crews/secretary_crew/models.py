

from typing import Optional
from pydantic import Field, BaseModel

class SecretaryCrewOutput(BaseModel):
    answer: str = Field(..., description="Generated response to the user's message")
    confidence: Optional[float] = Field(None, description="Confidence score of the generated response")

    delegate_to: Optional[str] = Field(
        None,
        description="""Specifies which agent or crew should handle the next step, if delegation is needed."""
    )
