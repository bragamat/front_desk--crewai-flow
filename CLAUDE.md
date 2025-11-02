# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **crewAI Flow** project that implements a **truly multilingual** front desk assistant system. The system:
- Accepts input in ANY language (50+ languages supported)
- Automatically detects the user's language
- Processes requests in English internally
- Responds back in the user's original language

The system uses multiple AI agent crews to handle conversations, detect languages, translate messages, and route requests to appropriate handlers.

## Key Commands

### Running the Project
```bash
# Start the flow (main entry point)
crewai run

# Alternative: using uv directly
uv run kickoff

# Visualize the flow graph
uv run plot
# Note: You may see a parsing warning for handle_search_topic - this is a known
# crewAI plot parser limitation and does not affect flow execution
```

### Development Setup
```bash
# Install dependencies
crewai install

# Or using uv directly
uv sync
```

### Environment Configuration
- Required: `OPENAI_API_KEY` in `.env` file
- Optional: `SERPAPI_API_KEY` for web search tools

## Architecture

### Flow Structure (main.py)

The project implements a **crewAI Flow** (`FrontDeskFlow`) that orchestrates multiple crews in sequence:

1. **run()** - Entry point (decorated with `@start()`)
2. **translate_user_message()** - Automatically detects ANY language and translates to English using `TranslationCrew`
3. **answer_user()** - Processes request using `SecretaryCrew` and routes to specialized crews if needed
4. **decide_next()** - Router that handles delegation or ends conversation

The flow is **completely language-agnostic** - it works identically whether the user speaks English, Spanish, French, Mandarin, Arabic, or any other language.

### State Management

`FrontDeskFlowState` (models/front_desk_state.py) maintains:
- `message`: Current message with content, role, and translation
- `history`: List of all messages exchanged
- `actions`: Actionable items to be performed (e.g., "search_topic")

The state flows through the entire conversation and is accessible via `self.state` in flow methods.

### Crew System

Two main crews handle different responsibilities:

**TranslationCrew** (crews/translation_crew/):
- Detects language, formality, and cultural context
- Translates user input to English
- Translates responses back to original language (when `reset=True`)
- Uses conditional tasks based on the `reset` flag

**SecretaryCrew** (crews/secretary_crew/):
- Classifies intent: FAQ, TECH, SCHEDULING, ACADEMICS, BILLING, SALES, GENERAL
- Uses knowledge sources from `knowledge/` directory (capabilities.md, actions.md)
- Returns structured output: `answer`, `confidence`, `delegate_to`
- Agent personality: friendly, casual, front desk assistant for "Mateus Braga's ecosystem"

### Key Models

**Message** (models/message.py):
- `content`: Original message text
- `role`: "user" or "assistant"
- `translation`: English translation

**Actions/Actionable** (models/actions.py):
- Tracks actions that need to be performed
- Status: "pending", "in_progress", "completed"
- Actions like "search_topic" can be delegated to specialized crews

### Configuration Files

Crews use YAML configuration:
- `config/agents.yaml` - Agent roles, goals, backstory
- `config/tasks.yaml` - Task descriptions, expected outputs

### Knowledge Sources

The `knowledge/` directory contains markdown files loaded as knowledge sources:
- `capabilities.md` - What the system can do (e.g., "Search topic on the web")
- `actions.md` - Available actions and which crew handles them

## Delegation Architecture

### How Delegation Works (crewAI Flow Pattern)

The flow uses **string-based routing** following crewAI best practices:

**Normal Flow (No Delegation):**
```
User (any language) → translate_user_message → answer_user → translate back → User (same language)
```

**Delegation Flow:**
```
User (any language) → translate_user_message (→ English) →
answer_user (returns "SearchTopicCrew") → decide_next (returns "SearchTopicCrew") →
@listen("SearchTopicCrew") handle_search_topic (search + synthesize) →
translate back (→ user's language) → User (same language)
```

**Example Flow Executions:**

```
Spanish: "¿Quién ganó?" → English: "Who won?" → Search → English answer →
Spanish: "Derek Lunsford ganó"

French: "Qui a gagné?" → English: "Who won?" → Search → English answer →
French: "Derek Lunsford a gagné"

Japanese: "誰が勝ちましたか？" → English: "Who won?" → Search → English answer →
Japanese: "Derek Lunsfordが勝ちました"
```

### Key Implementation Details (crewAI Best Practices)

1. **@router returns crew names directly as actions**
   ```python
   @router(answer_user)
   def decide_next(self, result: str):
       # Secretary returns exact crew name from knowledge base
       available_crews = ["SearchTopicCrew"]
       if result in available_crews:
           return result  # Use crew name directly as action
       return None  # End flow
   ```

2. **@listen uses crew names as string actions**
   ```python
   @listen("SearchTopicCrew")  # Listen for exact crew name
   def handle_search_topic(self):
       # Execute search
   ```

3. **Knowledge base defines available crews**
   - `capabilities.md` and `actions.md` specify exact crew names
   - SecretaryCrew returns the exact crew name (e.g., "SearchTopicCrew")
   - Router validates and passes crew name as action
   - Handler listens for that exact crew name

**Adding a New Delegation Crew:**
1. Add crew name to `available_crews` list in router
2. Add `@listen("YourCrewName")` handler method
3. Update knowledge files with the crew name and when to use it

### Critical: Passing Context to Crews

CrewAI crews don't automatically access flow state or history. You must explicitly pass data:

```python
# ❌ WRONG - Secretary won't see search results
secretary: CrewOutput = crew.kickoff(inputs={
    "message": "Synthesize the search results"
})

# ✅ CORRECT - Include results directly in message
secretary: CrewOutput = crew.kickoff(inputs={
    "message": f"""User asked: "{question}"

Search results:
{search_results}

Provide answer based on above."""
})
```

## Development Patterns

### Adding a New Delegation Crew

**Example: Adding a "SchedulingCrew"**

1. **Create the crew** under `src/frontdesk/crews/scheduling_crew/`
   - Implement crew class with `@CrewBase` decorator
   - Define agents with `@agent` decorator
   - Define tasks with `@task` decorator
   - Create `config/agents.yaml` and `config/tasks.yaml`

2. **Add to flow** in `main.py`:
   ```python
   # In router
   available_crews = ["SearchTopicCrew", "SchedulingCrew"]

   # Add listener
   @listen("SchedulingCrew")
   def handle_scheduling(self):
       # Your scheduling logic
   ```

3. **Update knowledge base** in `knowledge/actions.md`:
   ```markdown
   - Scheduling should be handled by SchedulingCrew
     - When delegating, use exact string: "SchedulingCrew"
   ```

### Flow Listeners and Routers

- `@listen("action_name")` - Executes when action_name is triggered
- `@router(method_name)` - Returns action string or None to end
- Methods can access and modify `self.state`
- **Use crew names directly** as action names for delegation

### Pydantic Output

Crews can return structured output using `output_pydantic` parameter:
- Access via `result.pydantic` or dictionary-style `result['field_name']`
- Enables type-safe data extraction from crew outputs

## Truly Language-Agnostic Design

**Important**: This system has **ZERO language bias**. It doesn't assume or prefer any specific language:

- ✅ No hardcoded language assumptions
- ✅ Automatic language detection for 50+ languages
- ✅ Internal processing always in English (for consistency and tool compatibility)
- ✅ Output always in the user's original language
- ✅ Works identically for Spanish, French, Arabic, Mandarin, etc.

The TranslationCrew acts as a universal adapter, making the entire system language-independent.

## Testing Multilingual Support

To test the flow with different languages, modify the message content in `main.py`:

```python
# Spanish
"content": "¿Quién ganó el último Mr. Olympia?"

# French
"content": "Qui a gagné le dernier Mr. Olympia?"

# German
"content": "Wer hat den letzten Mr. Olympia gewonnen?"

# Japanese
"content": "最新のミスターオリンピアは誰が勝ちましたか？"

# Arabic (RTL)
"content": "من فاز بآخر مستر أولمبيا؟"
```

The system will:
1. Automatically detect the language
2. Translate to English for processing
3. Perform any necessary actions (search, schedule, etc.)
4. Translate the response back to the original language

## Project Structure Notes

- Python version: >=3.10 <3.14
- Dependency manager: uv (faster alternative to pip)
- Framework: crewAI with Flow pattern
- Tools: crewai-tools with serpapi support
- Vector store: qdrant-client for embeddings
- **Language Support**: 50+ languages via TranslationCrew
