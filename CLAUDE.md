# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Resume Assistant Telegram Bot that helps users optimize their resumes for job applications by analyzing gaps between their profile and job vacancies. The system integrates with HeadHunter.ru API and uses OpenAI's GPT-4 for intelligent analysis and content generation.

## Architecture

The application follows a modular Python architecture with these main components:

- **Telegram Bot** (`src/tg_bot/`) - User interface using aiogram 3.x with FSM state management
- **OAuth Server** (`src/callback_local_server/`) - FastAPI server for HeadHunter.ru OAuth callbacks
- **HeadHunter Integration** (`src/hh/`) - API client, authentication, and token management
- **LLM Services** (`src/llm_*/`) - Specialized AI processors for different analysis types:
  - `llm_gap_analyzer` - Resume-vacancy gap analysis
  - `llm_cover_letter` - Personalized cover letter generation
  - `llm_interview_checklist` - Interview preparation checklists
  - `llm_interview_simulation` - Mock interview simulation with PDF reports
- **Data Models** (`src/models/`) - Pydantic models for structured data validation
- **Parsers** (`src/parsers/`) - Data extraction from HeadHunter API responses

## Configuration

The project uses environment variables for configuration. Copy `env_example.sh` to create your environment file:

```bash
cp env_example.sh .env
# Edit .env with your actual API keys and tokens
```

Required environment variables:
- `TG_BOT_BOT_TOKEN` - Telegram bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL_NAME` - OpenAI model (default: gpt-4)
- `HH_CLIENT_ID` - HeadHunter.ru application client ID
- `HH_CLIENT_SECRET` - HeadHunter.ru application client secret
- `HH_REDIRECT_URI` - OAuth callback URL (default: http://localhost:8080/callback)

## Running the Application

### Prerequisites
Install dependencies from `DOCS/requirements_file.txt`:
```bash
pip install -r DOCS/requirements_file.txt
```

### Start the Services

1. **Start OAuth callback server** (required for HeadHunter.ru authentication):
```bash
python -m src.callback_local_server.main
```

2. **Start Telegram bot** (in separate terminal):
```bash
python -m src.tg_bot.main
```

The OAuth server must be running before users can authenticate with HeadHunter.ru.

## Development Commands

### Running Debug Scripts
The `tests/` directory contains comprehensive debugging utilities for each LLM service. Each debug module includes:

**Gap Analysis Debug Tools:**
```bash
# Test data formatting
python tests/debug_gap/debug_formatter.py
# Test prompt generation
python tests/debug_gap/debug_gap_prompts.py
# Test LLM response generation
python tests/debug_gap/debug_gap_response.py
# Test Telegram message formatting
python tests/debug_gap/debug_gap_handler.py
# Test data parsing
python tests/debug_gap/debug_parsing.py
```

**Cover Letter Debug Tools:**
```bash
# Test data formatting
python tests/debug_cover/debug_cover_letter_formatter.py
# Test prompt generation
python tests/debug_cover/debug_cover_letter_prompts.py
# Test LLM response generation
python tests/debug_cover/debug_cover_letter_response.py
# Test Telegram message formatting
python tests/debug_cover/debug_cover_letter_handler.py
```

**Interview Checklist Debug Tools:**
```bash
# Test data formatting
python tests/debug_interview_checklist/debug_interview_checklist_formatter.py
# Test prompt generation
python tests/debug_interview_checklist/debug_interview_checklist_prompts.py
# Test LLM response generation
python tests/debug_interview_checklist/debug_interview_checklist_response.py
# Test Telegram message formatting
python tests/debug_interview_checklist/debug_interview_checklist_handler.py
```

Each debug tool creates JSON response files for testing subsequent tools in the pipeline.

### Linting and Formatting
Based on requirements_file.txt, the project supports:
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Import sorting
isort src/ tests/

# Type checking
mypy src/
```

### Testing
Run tests using pytest:
```bash
pytest tests/
```

## Key Development Patterns

### LLM Service Structure
All LLM services follow the same pattern:
- `config.py` - OpenAI configuration and settings
- `formatter.py` - Data formatting for prompts
- Main service file - Core logic and API interaction

### State Management
User state is managed through aiogram FSM with these key states:
- `UNAUTHORIZED` - User needs to authenticate with HH.ru
- `AUTHORIZED` - User can access all features
- `RESUME_PREPARATION` - Processing resume data
- `VACANCY_PREPARATION` - Processing vacancy data
- Service-specific states for each analysis type

### Data Flow
1. User authenticates via OAuth with HeadHunter.ru
2. User provides resume and vacancy links/IDs
3. Data is parsed into Pydantic models
4. LLM services process the structured data
5. Results are formatted and returned to user
6. Interview simulation generates PDF reports

### Error Handling
- All API calls include proper error handling and logging
- User state is preserved across errors
- Comprehensive logging to `LOGS/` directory with service-specific log files

## Important Notes

- The application stores user data only in memory (no persistent database)
- OAuth tokens are temporarily stored during user sessions
- PDF generation requires DejaVu fonts (included in `fonts/` directory)
- All LLM responses are validated through Pydantic models for type safety