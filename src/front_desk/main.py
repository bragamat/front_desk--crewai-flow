#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

class FrontDeskState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


class FrontDeskFlow(Flow[FrontDeskState]):

    @start()
    def run(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(run)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)


def kickoff():
    poem_flow = FrontDeskFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = FrontDeskFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
