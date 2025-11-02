# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **crewAI Flow** project that implements a multilingual front desk assistant system. The system uses multiple AI agent crews to handle conversations, detect languages, translate messages, and route requests to appropriate handlers.

## Key Commands

### Running the Project
```bash
# Start the flow (main entry point)
crewai run

# Alternative: using uv directly
uv run kickoff

# Visualize the flow graph
uv run plot
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
2. **translate_user_message()** - Detects language and translates to English using `TranslationCrew`
3. **answer_user()** - Processes request using `SecretaryCrew` and translates response back
4. **decide_next()** - Router that continues or ends conversation

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

### How Delegation Works

The flow uses a router-based delegation system that allows the SecretaryCrew to delegate tasks to specialized crews:

**Normal Flow (No Delegation):**
```
translate_user_message → answer_user → decide_next → (end/continue)
```

**Delegation Flow:**
```
translate_user_message → answer_user (returns delegation target) →
decide_next (routes to handler) → handle_search_topic (executes specialist crew) →
provide_final_answer_with_context (secretary synthesizes) → (translation & return)
```

### Key Implementation Details

1. **answer_user()**: When SecretaryCrew sets `delegate_to`, it returns the delegation target string instead of translating immediately
2. **decide_next()**: Router checks the return value and routes to appropriate handler (e.g., `handle_search_topic`)
3. **Handler method**: Executes specialist crew, stores results in `self.state.message.content`
4. **provide_final_answer_with_context()**: SecretaryCrew receives search results directly in the message and synthesizes final answer

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

### Adding a New Crew

1. Create crew directory under `src/frontdesk/crews/`
2. Implement crew class with `@CrewBase` decorator
3. Define agents with `@agent` decorator
4. Define tasks with `@task` decorator
5. Define crew with `@crew` decorator
6. Create `config/agents.yaml` and `config/tasks.yaml`
7. Define output model in `models.py`
8. Integrate into flow in `main.py`

### Flow Listeners and Routers

- `@listen(method_name)` - Executes after specified method
- `@router(method_name)` - Returns next method to execute or None to end
- Methods can access and modify `self.state`

### Pydantic Output

Crews can return structured output using `output_pydantic` parameter:
- Access via `result.pydantic` or dictionary-style `result['field_name']`
- Enables type-safe data extraction from crew outputs

## Project Structure Notes

- Python version: >=3.10 <3.14
- Dependency manager: uv (faster alternative to pip)
- Framework: crewAI with Flow pattern
- Tools: crewai-tools with serpapi support
- Vector store: qdrant-client for embeddings
