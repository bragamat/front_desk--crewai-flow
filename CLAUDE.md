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
