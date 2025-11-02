#!/usr/bin/env python
from datetime import datetime
from crewai import CrewOutput
from crewai.flow import Flow, listen, router, start

from frontdesk.crews import TranslationCrew, SecretaryCrew, SearchTopicCrew
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

        delegation = secretary['delegate_to']

        if delegation:
            if self.state.actions:  # type: ignore
                self.state.actions.add_action(action=delegation)

            self.state.message.content = secretary['answer']
            return delegation

        translator = TranslationCrew(reset=True).crew()
        translation: CrewOutput = translator.kickoff(inputs={
            "content": secretary['answer'],
            "history": [m.model_dump() for m in self.state.history],
        })

        self.state.add_assistant_message(
            content=secretary['answer'],
            translation=translation['output'],
        )
        return secretary['delegate_to']

    @router(answer_user)
    def decide_next(self, result: str):
        """Router that handles delegation based on crew name from secretary"""

        if result == "SearchTopicCrew":
            return "search_topic_crew"


        # No delegation, conversation complete
        return None

    @listen("search_topic_crew")
    def handle_search_topic(self):
        """Handle search topic delegation and synthesize answer"""
        print("\n" + "="*80)
        print("🔍 EXECUTING SEARCH TOPIC CREW")
        print("="*80 + "\n")

        # Extract topic from the user's translated message
        topic = self.state.message.translation
        current_year = datetime.now().year

        # Execute SearchTopicCrew
        search_crew = SearchTopicCrew().crew()
        search_result: CrewOutput = search_crew.kickoff(inputs={
            "topic": topic,
            "current_year": current_year,
        })

        # Store search results in state
        print("\n" + "="*80)
        print("📊 SEARCH RESULTS:")
        print(search_result.raw)
        print("="*80 + "\n")

        # Store search results temporarily for the next step
        search_results = search_result.raw

        # Add search results to history for context
        self.state.add_assistant_message(
            content=f"[SEARCH RESULTS FOR: {topic}]\n\n{search_results}",
            translation=None,
        )

        # Now synthesize answer using search results
        print("\n" + "="*80)
        print("💬 SECRETARY PROVIDING FINAL ANSWER WITH CONTEXT")
        print("="*80 + "\n")

        # Get the original question
        original_question = self.state.history[0].translation if self.state.history else "the user's question"

        # Ask secretary to synthesize answer using search results
        crew = SecretaryCrew().crew()
        secretary: CrewOutput = crew.kickoff(inputs={
            "message": f"""The user asked: "{original_question}"

Here are the search results:

{search_results}

Based on these search results, provide a clear, concise answer to the user's question. Focus on directly answering what they asked for - don't mention that you're searching or delegating. Just provide the answer based on the information above.""",
        })

        if secretary.pydantic is None:
            raise ValueError("Expected pydantic output from SecretaryCrew")

        # Translate back to user's language
        translator = TranslationCrew(reset=True).crew()
        translation: CrewOutput = translator.kickoff(inputs={
            "content": secretary['answer'],
            "history": [m.model_dump() for m in self.state.history],
        })

        self.state.add_assistant_message(
            content=secretary['answer'],
            translation=translation['output'],
        )

        print("\n" + "="*80)
        print("ENGLISH ANSWER:", secretary['answer'])
        print("TRANSLATED ANSWER:", translation['output'])
        print("="*80 + "\n")




def kickoff():
    """
    Example kickoff - demonstrates multilingual support.
    The flow automatically detects the input language and responds in the same language.

    Try any language:
    - Portuguese: "Quem ganhou o ultimo Mr. Olympia?"
    - Spanish: "¿Quién ganó el último Mr. Olympia?"
    - French: "Qui a gagné le dernier Mr. Olympia?"
    - German: "Wer hat den letzten Mr. Olympia gewonnen?"
    - English: "Who won the last Mr. Olympia?"
    """
    poem_flow = FrontDeskFlow()
    poem_flow.kickoff(inputs={
        "message": {
            # Example in Spanish (change to any language to test)
            "content": "Hola, ¿quién ganó el último Mr. Olympia en la categoría Classic Physique?",
            "role": "user"
        }
    })

def plot():
    poem_flow = FrontDeskFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
