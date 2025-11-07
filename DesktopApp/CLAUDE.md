# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HWPX Desktop Converter**: A Windows desktop application (PyQt5) that converts Markdown documents to high-quality HWPX files using the pyhwpx library and native Hancom Office 2024 automation. This app connects to the HWP Report Generator backend API for authentication and retrieving Markdown artifacts.

## Technology Stack

- **UI Framework**: PyQt5 5.15+ with qt-material theming
- **Python**: 3.10+ (3.12 recommended)
- **HWP Automation**: pyhwpx 1.6.6+ (Windows only, requires Hancom Office 2024)
- **HTTP Client**: requests 2.31+
- **Platform**: Windows 11 x64
- **External Dependency**: Hancom Office 2024 (한컴오피스 2024)

## Architecture

### Core Components

1. **UI Layer** (`src/ui/`)
   - `login_window.py` - User authentication
   - `settings_window.py` - Configuration (API URL, HWP path, theme)
   - `main_window.py` - File selection and conversion UI
   - `progress_dialog.py` - Conversion progress tracking
   - `theme.py` - Material theme management

2. **API Layer** (`src/api/`)
   - `client.py` - Backend API integration (requests-based)
   - `token_manager.py` - JWT token storage (encrypted with Windows DPAPI)
   - `session_manager.py` - Session persistence and auto-login

3. **Conversion Engine** (`src/converter/`)
   - `engine.py` - pyhwpx wrapper for MD → HWPX conversion
   - `markdown_parser.py` - Reused from backend (parses MD structure)

4. **Configuration** (`src/config.py`)
   - `AppSettings` - Dataclass for user preferences
   - `SettingsStore` - Load/save settings to `%APPDATA%\HWPConverter\settings.json`

5. **Logging** (`src/logging/`)
   - `logger.py` - Centralized logging to `%APPDATA%\HWPConverter\logs\`
   - Supports "운영" (operational) and "디버그" (debug) modes

### Data Flow

1. User launches app → `main.py` → Load settings
2. First run → Show Settings Window (configure API URL, HWP path)
3. Login → Store JWT token (encrypted) + session info
4. Main Window → Fetch topics → Select artifacts (MD files)
5. Convert → Download MD → pyhwpx conversion → Save HWPX locally

### File Locations

| Data | Path |
|------|------|
| **Settings** | `%APPDATA%\HWPConverter\settings.json` |
| **Session** | `%APPDATA%\HWPConverter\session.json` (JWT + refresh token) |
| **Logs** | `%APPDATA%\HWPConverter\logs\application.log` |
| **HWP Path** | Default: `C:\Program Files\Hnc\Hwp2024\Hwp.exe` |

## Development Commands

### Environment Setup

```powershell
# From repository root
cd DesktopApp

# Create virtual environment (uv recommended)
uv venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Run Application

```powershell
# From DesktopApp directory with venv activated
uv run python -m src.main

# Or if venv is already activated
python -m src.main
```

### Environment Verification

Check if all prerequisites are met (Hancom Office, pywin32, etc.):

```powershell
python scripts\verify_environment.py
```

This script validates:
- Python version (3.10+)
- Required packages (PyQt5, pyhwpx, etc.)
- Hancom Office 2024 installation
- pywin32 COM extensions

### Testing

```powershell
# Run conversion test (requires running backend)
python -m pytest tests/ -v

# Test HWP path detection
python -c "from src.config import SettingsStore; print(SettingsStore.detect_hwp_path())"
```

## Configuration

### Settings File Structure

`%APPDATA%\HWPConverter\settings.json`:

```json
{
  "api_base_url": "http://localhost:8000",
  "hwp_install_path": "C:\\Program Files\\Hnc\\Hwp2024\\Hwp.exe",
  "default_save_path": "C:\\Users\\{user}\\Documents\\HWP Reports",
  "auto_detect_hwp": true,
  "material_theme": "dark_teal",
  "log_mode": "운영"
}
```

### Environment Variables (Optional)

While not required, you can override settings via environment:

```powershell
# Override API URL for testing
$env:HWP_API_URL = "http://localhost:8000"
python -m src.main
```

## Key Design Patterns

### Settings Management

The app uses a two-layer config system:
1. **Defaults** (`config.py` constants) - Fallback values
2. **User Settings** (`settings.json`) - Persisted preferences

```python
# src/config.py
@dataclass
class AppSettings:
    api_base_url: str = "http://localhost:8000"
    hwp_install_path: str = r"C:\Program Files\Hnc\Hwp2024\Hwp.exe"
    # ...

class SettingsStore:
    @classmethod
    def load(cls) -> AppSettings:
        """Load from JSON, fallback to defaults"""
```

**Important**: Always use `SettingsStore.load()` instead of hardcoding paths.

### Token Security

JWT tokens are encrypted using Windows DPAPI (`win32crypt.CryptProtectData`):

```python
# src/api/token_manager.py
def save_token(token: str):
    encrypted = win32crypt.CryptProtectData(token.encode())
    # Save encrypted bytes to file
```

**Security note**: DPAPI encryption is user-scoped, so tokens cannot be decrypted by other Windows users.

### pyhwpx Conversion

The engine uses Hancom Office's COM automation API:

```python
# src/converter/engine.py
hwp = Hwp()
hwp.XHwpWindows.Item(0).Visible = False  # Background mode

# Apply CharShape (font, size, bold)
hwp.HParameterSet.HCharShape.FontName = "맑은 고딕"
hwp.HParameterSet.HCharShape.FontSize = 16
hwp.HAction.Execute("CharShape", hwp.HParameterSet.HCharShape.HSet)

# Insert text
hwp.HParameterSet.HInsertText.Text = "제목"
hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
```

**Critical**: Always call `hwp.Quit()` in a `finally` block to release COM resources.

## Common Tasks

### Adding a New Setting

1. Update `AppSettings` dataclass in `config.py`:
   ```python
   @dataclass
   class AppSettings:
       # ...
       new_setting: str = "default_value"
   ```

2. Add UI field in `settings_window.py`:
   ```python
   self.new_setting_input = QLineEdit(settings.new_setting)
   layout.addRow("New Setting:", self.new_setting_input)
   ```

3. Save/load logic is handled automatically by `SettingsStore.to_dict()` / `from_dict()`.

### Adding a New API Endpoint

Update `api/client.py`:

```python
class APIClient:
    def new_endpoint(self, param: str) -> dict:
        """Call new API endpoint"""
        response = self.session.get(
            f"{self.base_url}/api/new-endpoint",
            params={"param": param}
        )
        response.raise_for_status()
        return response.json()
```

**Important**: All API methods should:
- Use `self.session` (includes auth headers)
- Call `raise_for_status()` for error handling
- Return parsed JSON (not raw response)

### Customizing Material Themes

Available themes are in qt-material package. Current default: `dark_teal`.

To change:
1. Settings Window → Material 테마 dropdown
2. Select theme (auto-applies preview)
3. Click Save

Programmatic change:

```python
from src.ui.theme import apply_theme
apply_theme(app, "dark_blue.xml")
```

**Note**: Don't include `.xml` extension in settings (added automatically).

## Troubleshooting

### "한컴오피스 2024가 설치되어 있지 않습니다"

**Cause**: pyhwpx cannot find Hancom Office COM server.

**Solutions**:
1. Run `scripts\verify_environment.py` to check installation
2. Settings Window → "자동 탐지" button (auto-detect HWP path)
3. Manually set path: `C:\Program Files\Hnc\Hwp2024\Hwp.exe`
4. Verify COM registration: `regsvr32 /s "C:\Program Files\Hnc\Hwp2024\HwpCtrl.dll"`

### "API 연결 실패"

**Cause**: Backend server not running or incorrect URL.

**Solutions**:
1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Settings Window → API URL → "연결 테스트" button
3. Check firewall/proxy settings
4. Verify URL format: `http://localhost:8000` (no trailing slash)

### Token Expired / Auto-login Failed

**Cause**: JWT token lifetime exceeded or refresh token invalid.

**Solutions**:
1. Delete session file: `%APPDATA%\HWPConverter\session.json`
2. Restart app → Manual login
3. Backend setting: Increase `JWT_EXPIRE_MINUTES` in backend `.env`

### Conversion Hangs

**Cause**: Hancom Office process not terminating properly.

**Solutions**:
1. Kill background processes: `taskkill /F /IM Hwp.exe`
2. Check logs: `%APPDATA%\HWPConverter\logs\application.log`
3. Reduce concurrent conversions (currently single-threaded)

### Theme Not Applying

**Cause**: qt-material theme file not found or syntax error.

**Solutions**:
1. Verify theme name (without `.xml`): `dark_teal`, `dark_blue`, etc.
2. Check available themes: `python -c "from qt_material import list_themes; print(list_themes())"`
3. Reset to default: Delete `settings.json` → Restart app

## Dependencies Explained

| Package | Purpose | Windows-Only? |
|---------|---------|---------------|
| **PyQt5** | Desktop UI framework | No |
| **qt-material** | Material Design themes | No |
| **requests** | HTTP API client | No |
| **pyhwpx** | Hancom Office COM automation | **Yes** |
| **pywin32** | Windows API (DPAPI, COM) | **Yes** |
| **python-dotenv** | Load `.env` (optional) | No |

**Deployment note**: When packaging with PyInstaller, ensure `pywin32` COM extensions are included via `--hidden-import` flags.

## Backend API Integration

This app consumes the following backend endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/login` | POST | JWT authentication |
| `/api/auth/me` | GET | Verify token, get user info |
| `/api/topics` | GET | List user's topics |
| `/api/artifacts/topics/{id}` | GET | Get artifacts for topic (filter: `kind=md`) |
| `/api/artifacts/{id}/content` | GET | Download Markdown content |

**API versioning**: App expects backend v2.0+. Check compatibility via `/api/version` (if implemented).

## Project Structure

```
DesktopApp/
├── src/
│   ├── main.py                  # Entry point (calls bootstrap())
│   ├── config.py                # AppSettings, SettingsStore, constants
│   ├── ui/
│   │   ├── login_window.py      # LoginWindow (QDialog)
│   │   ├── settings_window.py   # SettingsWindow (QDialog)
│   │   ├── main_window.py       # MainWindow (conversion workflow, progress UI)
│   │   ├── progress_dialog.py   # Progress dialog with cancel support
│   │   └── theme.py             # apply_theme()
│   ├── api/
│   │   ├── client.py            # APIClient (requests wrapper)
│   │   ├── token_manager.py     # Token encryption (DPAPI)
│   │   └── session_manager.py   # Session persistence
│   ├── converter/
│   │   ├── engine.py            # ConverterEngine (pyhwpx)
│   │   └── markdown_parser.py   # parse_markdown_to_content()
│   └── logging/
│       └── logger.py            # get_logger(), setup_logging()
├── scripts/
│   ├── convert_batch.py         # Batch conversion / dry-run parser
│   └── verify_environment.py    # Environment checker
├── doc/                         # Design documents (Korean)
├── requirements.txt             # Python dependencies
├── README.md                    # User guide
└── CLAUDE.md                    # This file
```

## Development Phases

The project follows a phased implementation (see `doc/08.hwpxDesktopApp.md`):

- **Phase 1**: Authentication (Login, Settings) - ✅ Complete
- **Phase 2**: File management (Topic/Artifact selection) - ✅ Complete
- **Phase 3**: Conversion engine (pyhwpx integration) - ✅ Complete
- **Phase 4**: Packaging (PyInstaller .exe) - 🚧 In Progress
- **Phase 5**: Auto-update, batch optimization - 📋 Planned

## Coding Standards

### Docstrings

Follow Google-style docstrings:

```python
def convert_to_hwpx(md_content: str, output_path: str) -> bool:
    """Convert Markdown to HWPX using pyhwpx.

    Args:
        md_content: Raw Markdown text
        output_path: Target HWPX file path

    Returns:
        True if conversion succeeded, False otherwise

    Raises:
        FileNotFoundError: If HWP executable not found
        ValueError: If MD content is empty
    """
```

### Error Handling

Always use try-except with user-friendly messages:

```python
try:
    result = api_client.get_topics()
except requests.exceptions.ConnectionError:
    QMessageBox.warning(self, "연결 오류", "서버에 연결할 수 없습니다.")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    QMessageBox.critical(self, "오류", f"예상치 못한 오류가 발생했습니다:\n{e}")
```

### Logging

Use structured logging with context:

```python
from src.logging.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting conversion", extra={"file_count": len(files)})
logger.error("Conversion failed", extra={"artifact_id": 123, "error": str(e)})
```

**Log levels**:
- `DEBUG` - Detailed diagnostic (only in "디버그" mode)
- `INFO` - General informational messages
- `WARNING` - Recoverable issues (e.g., auto-retry succeeded)
- `ERROR` - Failures requiring user attention

## Testing Strategy

### Manual Testing Checklist

Before committing major changes, verify:

- [ ] Settings: Save → Restart → Load (persistence)
- [ ] Login: Correct credentials → JWT stored → Auto-login works
- [ ] Main Window: Select topic → Artifacts load → Checkboxes work
- [ ] Conversion: Select files → Convert → HWPX opens in Hancom
- [ ] Theme: Change theme → Preview applies → Restart → Theme persists
- [ ] Error Handling: Disconnect backend → Friendly error messages

### Automated Testing

- `py -3 -m pytest DesktopApp\tests -v` → Markdown 파서와 변환 엔진 스텁 검증
- `python DesktopApp\scripts\convert_batch.py docs --dry-run` → Markdown 파싱 품질 점검
- `python DesktopApp\scripts\convert_batch.py docs --recursive --output build\hwpx` → 실환경 일괄 변환 (pyhwpx 필요)

## Related Documentation

- **Root CLAUDE.md** - Backend/frontend web app development
- **Backend API Docs** - `/docs` (Swagger UI) when backend is running
- **pyhwpx Docs** - https://github.com/choi-yong-oh/pyhwpx
- **PyQt5 Docs** - https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **Design Docs** - `doc/08.hwpxDesktopApp.md` (architecture, detailed flows)

---

**Last Updated**: 2025-11-05
**Version**: 1.0
**Target Environment**: Windows 11 + Python 3.10+ + Hancom Office 2024
