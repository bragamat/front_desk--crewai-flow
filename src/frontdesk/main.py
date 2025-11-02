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

        # Store delegation info in state for router to check
        delegation = secretary['delegate_to']

        if delegation:
            # Add action to track delegation
            if self.state.actions:  # type: ignore
                self.state.actions.add_action(action=delegation)

            print("\n" + "="*80)
            print("SECRETARY RESPONSE:", secretary['answer'])
            print("DELEGATED TO:", delegation)
            print("="*80 + "\n")

            # Don't translate yet - we'll translate after delegation completes
            # Store the intermediate answer in state
            self.state.message.content = secretary['answer']
            return delegation  # Return delegation target for router

        # No delegation - provide final answer
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

        return secretary['answer']

    @router(answer_user)
    def decide_next(self, result: str):
        """Router that handles delegation and conversation flow"""

        # Normalize the result for comparison
        normalized_result = result.lower().replace('_', '').replace(' ', '')

        # Check if this is a delegation request
        if normalized_result in ['searchtopicrew', 'searchtopic']:
            print("🔄 Routing to search topic handler...")
            return self.handle_search_topic

        # Add more delegation handlers here as needed
        # elif normalized_result == 'schedulingcrew':
        #     return self.handle_scheduling

        # Check if conversation should end
        if "bye" in result.lower():
            print("Conversation ended.")
            return None  # End the flow

        # Continue conversation - wait for next user message
        return self.translate_user_message

    @listen(decide_next)
    def handle_search_topic(self):
        """Handle search topic delegation"""
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

        # Store search results in state for secretary to use
        print("\n" + "="*80)
        print("📊 SEARCH RESULTS:")
        print(search_result.raw)
        print("="*80 + "\n")

        # Store search results temporarily for the next step
        # We'll use this to pass to the secretary
        self.state.message.content = search_result.raw

        # Add search results to history for context
        self.state.add_assistant_message(
            content=f"[SEARCH RESULTS FOR: {topic}]\n\n{search_result.raw}",
            translation=None,
        )

        # Now route to provide final answer with search context
        return self.provide_final_answer_with_context()

    def provide_final_answer_with_context(self):
        """Secretary provides final answer using search results"""
        print("\n" + "="*80)
        print("💬 SECRETARY PROVIDING FINAL ANSWER WITH CONTEXT")
        print("="*80 + "\n")

        # Get the original question and search results
        original_question = self.state.history[0].translation if self.state.history else "the user's question"
        search_results = self.state.message.content

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

        return secretary['answer']



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
