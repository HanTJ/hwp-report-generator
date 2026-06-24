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

**Main Content Placeholders:**
- `{{TITLE}}` - Report title
- `{{DATE}}` - Generation date
- `{{BACKGROUND}}` - Background and purpose section content
- `{{MAIN_CONTENT}}` - Main body content
- `{{CONCLUSION}}` - Conclusion and recommendations content
- `{{SUMMARY}}` - Executive summary content

**Section Title Placeholders:**
- `{{TITLE_BACKGROUND}}` - Background section heading (default: "배경 및 목적")
- `{{TITLE_MAIN_CONTENT}}` - Main content section heading (default: "주요 내용")
- `{{TITLE_CONCLUSION}}` - Conclusion section heading (default: "결론 및 제언")
- `{{TITLE_SUMMARY}}` - Summary section heading (default: "요약")

Note: Section title placeholders allow customization of section headings while maintaining consistent template structure.

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

### Line Break Handling in HWPX

The system implements a sophisticated approach to handle line breaks in HWPX format:

1. **Paragraph Separation**: Double line breaks (`\n\n`) split text into separate `<hp:p>` (paragraph) tags
2. **Line Break Tags**: Single line breaks (`\n`) within paragraphs are converted to `<hp:lineBreak/>` XML tags
3. **Layout Cleanup**: Automatically removes incomplete `<hp:linesegarray>` elements that would prevent proper rendering
4. **Auto-calculation**: Hangul Word Processor automatically recalculates layout information when opening files without linesegarray data

This ensures that generated reports display with proper line breaks when opened in Hangul Word Processor, without requiring manual layout calculations.

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
