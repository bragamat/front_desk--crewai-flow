"""Translation Crew for Multilingual Conversations"""

from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.conditional_task import ConditionalTask
from crewai.project import CrewBase, agent, task, crew

from frontdesk.crews.translation_crew.models import TranslationCrewOutput

@CrewBase
class TranslationCrew:
    agents: List[BaseAgent]
    tasks: List[Task]
    tools: Optional[List] = None

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, reset = False) -> None:
        super().__init__()
        self.reset = reset

    @agent
    def language_detector(self) -> Agent:
        """Language Detector Agent"""
        return Agent(
            config=self.agents_config["language_detector"], # type: ignore
        )

    @task
    def detect_language(self) -> Task:
        """Detect Language Task"""
        return Task(
            config=self.tasks_config["detect_language"], # type: ignore
            output_pydantic=TranslationCrewOutput
        )

    @task
    def translate_to_original(self) -> ConditionalTask:
        """Translate to Original Language Task"""
        return ConditionalTask(
            config=self.tasks_config["translate_to_original"], # type: ignore
            condition=lambda _: self.reset is True, # type: ignore
            output_pydantic=TranslationCrewOutput
        )

    @crew
    def crew(self) -> Crew:
        """Create the Translation Crew"""
        return Crew(
            agents=self.agents, # type: ignore
            tasks=self.tasks, # type: ignore
            process=Process.sequential, # type: ignore
            verbose=True, # type: ignore
        ) 
