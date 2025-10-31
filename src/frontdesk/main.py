#!/usr/bin/env python
from crewai.flow import Flow, listen, start

from frontdesk.crews import TranslationCrew
from frontdesk.models import FrontDeskFlowState

class FrontDeskFlow(Flow[FrontDeskFlowState]):

    @start()
    def run(self):
        crew = TranslationCrew().crew()

        result = crew.kickoff(inputs={
            "content": self.state.message.content,
            "history": self.state.history,
        })

        print("result: ", result)


    @listen(run)
    def output(self):
        return self.state


def kickoff():
    poem_flow = FrontDeskFlow()
    poem_flow.kickoff(inputs={
        "message": {
            "content": "Eai, tudo bem? cara, pode me ajuar a traduzir esse texto para o ingles?",
            "role": "user"
        }
    })

def plot():
    poem_flow = FrontDeskFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
