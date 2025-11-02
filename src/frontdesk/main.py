#!/usr/bin/env python
from crewai import CrewOutput
from crewai.flow import Flow, listen, router, start

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
        secretary: CrewOutput = crew.kickoff(inputs={
            "message": self.state.message.translation,
        })

        if secretary.pydantic is None:
            raise ValueError("Expected pydantic output from SecretaryCrew")

        translator = TranslationCrew(reset=True).crew()
        translation: CrewOutput = translator.kickoff(inputs={
            "content": secretary['answer'],
            "history": [m.model_dump() for m in self.state.history],
        })

        self.state.add_assistant_message(
            content=secretary['answer'],
            translation=translation['output'],
        )

        if secretary.pydantic.delegate_to and self.state.actions:  # type: ignore
            self.state.actions.add_action(
                action=secretary['delegate_to'],
            )

        print("\n" + "="*80)
        print("ENGLISH ANSWER:", secretary['answer'])
        print("TRANSLATED ANSWER:", translation['output'])
        if secretary['delegate_to']:
            print("DELEGATED TO:", secretary['delegate_to'])
        print("="*80 + "\n")

        return secretary['answer']

    @router(answer_user)
    def decide_next(self, answer: str):
        if "bye" in answer.lower():
            print("Conversation ended.")
            return None  # End the flow
        else:
            return self.translate_user_message  # Listen for the next user message



def kickoff():
    poem_flow = FrontDeskFlow()
    poem_flow.kickoff(inputs={
        "message": {
            "content": """Eai, tudo bem? cara, queria saber quem ganhou o ultimo
            Mr. Olympia na categoria classic e Open""",
            "role": "user"
        }
    })

def plot():
    poem_flow = FrontDeskFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
