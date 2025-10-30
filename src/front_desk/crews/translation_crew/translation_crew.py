"""Translation Crew for Multilingual Conversations"""

from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class TranslationCrew:
    agents: List[BaseAgent]
    tasks: List[Task]
    tools: Optional[List] = None

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def language_detector(self) -> Agent:
        """Language Detector Agent"""
        return Agent(
            config=self.agents_config["language_detector"], # type: ignore
            verbose=False
        )

    @agent
    def conversation_partner(self) -> Agent:
        """Conversation Partner Agent"""
        return Agent(
            config=self.agents_config["conversation_partner"], # type: ignore
            tools=self.tools if hasattr(self, 'tools') and self.tools else [],
            verbose=False
        )

    @agent
    def response_optimizer(self) -> Agent:
        """Response Optimizer Agent"""
        return Agent(
            config=self.agents_config["response_optimizer"], # type: ignore
            verbose=False
        )

    @task
    def detect_language(self) -> Task:
        """Detect Language Task"""
        return Task(
            config=self.tasks_config["detect_language"], # type: ignore
        )

    @task
    def engage_conversation(self) -> Task:
        """Engage Conversation Task"""
        return Task(
            config=self.tasks_config["engage_conversation"], # type: ignore
        )

    @task
    def optimize_response(self) -> Task:
        """Optimize Response Task"""
        return Task(
            config=self.tasks_config["optimize_response"], # type: ignore
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
