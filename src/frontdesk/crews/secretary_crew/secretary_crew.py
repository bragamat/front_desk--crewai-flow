from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

from typing import List

from frontdesk.crews.secretary_crew.models import SecretaryCrewOutput
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

cap_source = TextFileKnowledgeSource(
    file_paths=["capabilities.md"],
)

@CrewBase
class SecretaryCrew():
    """SecretaryCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def frontdesk_responder(self) -> Agent:
        return Agent(
            config=self.agents_config['frontdesk_responder'], # type: ignore[index]
            verbose=True
        )

    @task
    def respond_user_input(self) -> Task:
        return Task(
            config=self.tasks_config['respond_user_input'], # type: ignore[index]
            output_pydantic=SecretaryCrewOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SecretaryCrew crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            knowledge_sources=[cap_source]
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
