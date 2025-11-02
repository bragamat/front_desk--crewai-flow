#!/usr/bin/env python
from crewai import CrewOutput
from crewai.flow import Flow, listen, start

from frontdesk.crews import TranslationCrew, SecretaryCrew 
from frontdesk.models import FrontDeskFlowState

class FrontDeskFlow(Flow[FrontDeskFlowState]):

    @start()
    def run(self):
        print("FrontDeskFlow started")

    @listen(run)
    def translate_user_message(self):
        crew = TranslationCrew().crew()
        result: CrewOutput = crew.kickoff(inputs={
            "content": self.state.message.content,
            "history": self.state.history,
        })

        if result.pydantic:
          self.state.message.translation = result['output']
          self.state.add_user_message(
                content=result['original'],
                translation=result['output'],
            )

    @listen(translate_user_message)
    def answer_user(self):
        crew = SecretaryCrew().crew()
        result: CrewOutput = crew.kickoff(inputs={
            "message": self.state.message.translation,
        })

        if result.pydantic:
            translator = TranslationCrew(reset=True).crew()
            translation: CrewOutput = translator.kickoff(inputs={
                "content": result['answer'],
                "history": [m.model_dump() for m in self.state.history],
            })

            self.state.add_assistant_message(
                content=result['answer'],
                translation=translation['output'],
            )

        print("Assistant's answer:", result['answer'])
        return result['answer']


def kickoff():
    poem_flow = FrontDeskFlow()
    poem_flow.kickoff(inputs={
        "message": {
            "content": """Eai, tudo bem? cara, pode me ajuar a traduzir esse texto
                para o ingles? ou melhor pode me falar quais sao suas capacidades?""",
            "role": "user"
        }
    })

def plot():
    poem_flow = FrontDeskFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
