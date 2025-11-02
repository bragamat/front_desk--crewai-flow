
from typing import List, Optional
from pydantic import BaseModel, Field

from frontdesk.models.actions import Actions
from frontdesk.models.message import Message

class FrontDeskFlowState(BaseModel):
    message: Message = Field(
        default_factory=Message,
        description="The latest message exchanged at the front desk"
    )

    actions: Optional[Actions] = Field(
        default_factory=Actions,
        description="The actions to be performed at the front desk"
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
