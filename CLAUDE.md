# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HWP Report Generator: A FastAPI-based web system that automatically generates Korean HWP (Hangul Word Processor) format reports using Claude AI. Users input a report topic and the system generates a complete report following a bank's internal form template.

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Package Manager**: uv (recommended) or pip
- **AI**: Claude API (Anthropic) - Model: claude-sonnet-4-5-20250929, anthropic==0.71.0
- **HWP Processing**: olefile, zipfile (HWPX format)
- **Templates**: Jinja2 (for web UI)
- **Frontend**: HTML/CSS/JavaScript (simple UI)

## Architecture

### Core Components

1. **main.py**: FastAPI application with endpoints for report generation
2. **utils/claude_client.py**: Claude API integration for content generation
3. **utils/hwp_handler.py**: HWPX file manipulation (unzip → modify XML → rezip)
4. **templates/report_template.hwpx**: HWP template with placeholders
5. **templates/index.html + static/**: Simple web UI for user input

### Data Flow

1. User submits report topic via web UI
2. FastAPI endpoint receives request
3. Claude API generates structured report content (title, summary, background, main content, conclusion)
4. HWP handler extracts HWPX (ZIP format), modifies XML content, replaces placeholders
5. System returns generated HWPX file for download

### HWP Template Placeholders

The HWPX template uses these placeholders that Claude's generated content replaces:
- `{{TITLE}}` - Report title
- `{{SUMMARY}}` - Executive summary
- `{{BACKGROUND}}` - Background and purpose
- `{{MAIN_CONTENT}}` - Main body content
- `{{CONCLUSION}}` - Conclusion and recommendations
- `{{DATE}}` - Generation date

## Environment Setup

Create `.env` file:
```
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

**Security**: Never commit `.env` file to git. Add to `.gitignore`.

## Development Commands

### Install dependencies:
**Using uv (recommended):**
```bash
uv pip install -r requirements.txt
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### Run development server:
**Using uv:**
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Using standard python:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the application:
```
http://localhost:8000       # Main UI
http://localhost:8000/docs  # API Documentation (Swagger)
```

## HWP File Handling Notes

- **Format**: Use HWPX (not HWP). HWPX is a ZIP archive containing XML files
- **Processing**: Unzip → Parse/modify XML → Rezip as HWPX
- **Compatibility**: HWPX format ensures cross-platform compatibility
- **Character encoding**: Ensure UTF-8 encoding for Korean text
- **Auto Template Generation**: If `templates/report_template.hwpx` doesn't exist, the system automatically creates a basic template on first report generation (main.py:113-161)

## Project Structure

```
hwp-report-generator/
├── main.py                    # FastAPI app with /generate endpoint
├── utils/
│   ├── claude_client.py       # Claude API client wrapper
│   └── hwp_handler.py         # HWPX file processor
├── templates/
│   ├── report_template.hwpx   # HWP template with placeholders
│   └── index.html             # Web interface
├── static/                    # CSS/JS assets
├── output/                    # Generated reports storage
└── temp/                      # Temporary file processing
```

## API Key Configuration

The system expects `CLAUDE_API_KEY` in environment variables. Check API usage limits and network connectivity if generation fails.
