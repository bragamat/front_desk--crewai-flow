
from typing import List, Literal, Optional

from pydantic import BaseModel, Field,ConfigDict

class Message(BaseModel):
    content: str = Field(default_factory=str, description="The content of the message")
    role: Optional[Literal['user', 'assistant']] = Field(default="user", description="The content of the message")
    translation: Optional[str] = Field(default=None, description="The translation of the message to english")

    
    model_config = ConfigDict(extra='allow')

class Actionable(BaseModel):
    done: bool = Field(default=False, description="Whether the action has been completed")
    action: str = Field(
        default_factory=str,
        description="""
          The action to be taken. This could be one of several predefined actions such as:
          - "search_topic"
          - "send_notification"
        """
    )
    started_at: Optional[str] = Field(default=None, description="The timestamp when the action was started")
    completed_at: Optional[str] = Field(default=None, description="The timestamp when the action was completed")


    # parameters: Optional[dict] = Field(default_factory=dict, description="The parameters for the action")
    model_config = ConfigDict(extra='allow')

class FrontDeskFlowState(BaseModel):
    message: Message = Field(
        default_factory=Message,
        description="The latest message exchanged at the front desk"
    )

    actions: Optional[List[Actionable]] = Field(
        default_factory=list,
        description="The list of actions taken at the front desk"
    )

    history: List[Message] = Field(
        default_factory=list,
        description="The history of messages exchanged at the front desk"
    )

    def add_user_message(self,
                    content: str,
                    translation: Optional[str] = None,
                    ):

        message = Message(content=content, translation=translation, role="user")

        self.history.append(message)
        return message

    def add_assistant_message(self,
                    content: str,
                    translation: Optional[str] = None,
                    ):
        message = Message(content=content, translation=translation, role="assistant")

        self.history.append(message)
        return message
