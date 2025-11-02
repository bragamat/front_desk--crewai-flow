from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

class Actionable(BaseModel):
    uid: UUID = Field(default_factory=uuid4, description="Unique identifier for the action")
    status: str = Field(
        default="pending",
        description="""
          The current status of the action. Possible values include:
          - "pending"
          - "in_progress"
          - "completed"
        """
    )
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

class Actions(BaseModel):
    actionables: list[Actionable] = Field(
        default_factory=list,
        description="A list of actions to be performed"
    )

    def add_action(self,
                    action: str,
                    done: bool = False,
                    started_at: Optional[str] = None,
                    completed_at: Optional[str] = None,
                    ):
        actionable = Actionable(
            action=action,
            status="completed" if done else "in_progress" if started_at else "pending",
            started_at=started_at,
            completed_at=completed_at,
        )
        self.actionables.append(actionable)

        return actionable



