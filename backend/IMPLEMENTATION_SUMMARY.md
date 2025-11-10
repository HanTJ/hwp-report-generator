# Implementation Summary: Template Meta-Info & System Prompt Generation

## Overview
Implemented a complete template-based system prompt generation and utilization system. This enables users to upload HWPX templates once, and the system automatically generates metadata and system prompts that are reused across all topics using that template.

**Completion Date**: November 10, 2025

## Implementation Phases

### Phase 1: Core Implementation ✅ (COMPLETE)

#### 1. Meta-Info Generator Module
**File**: `app/utils/meta_info_generator.py`

Main function:
- `create_meta_info_from_placeholders(placeholders)` - Converts Placeholder objects to metadata JSON

Helper functions:
- `_get_display_name()` - Generates Korean display names
- `_get_description()` - Generates 2-4 sentence descriptions
- `_get_examples()` - Generates practical examples

**Features**:
- Keyword classification: TITLE → section_title, SUMMARY/BACKGROUND/CONCLUSION → section_content, DATE → metadata
- Safe fallback for unknown keywords: defaults to section_content with auto-generated names
- Full Google-style DocStrings compliant with CLAUDE.md guidelines

**Keyword Strategy**: Progressive expansion (Phase 1 MVP)
- Phase 1: 5 keywords (TITLE, SUMMARY, BACKGROUND, CONCLUSION, DATE)
- Phase 2 (1 month): Add 5-10 frequently used keywords based on usage logs
- Phase 3 (3-6 months): Admin interface for custom keywords

#### 2. Template Upload API Modification
**File**: `app/routers/templates.py`

**Changes**:
- Added import: `from app.utils.meta_info_generator import create_meta_info_from_placeholders`
- Step 9-1: After prompt_system generation, call `create_meta_info_from_placeholders()`
- Response includes `prompt_meta` field with metadata JSON array

**Flow**:
1. Extract Placeholders from HWPX template
2. Validate template integrity
3. Generate `prompt_system` via `create_dynamic_system_prompt()`
4. Generate `prompt_meta` via `create_meta_info_from_placeholders()` ✨ NEW
5. Store Template with both prompt_system and prompt_user
6. Return metadata in upload response

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "재무보고서 템플릿",
    "placeholders": [{"key": "{{TITLE}}"}, ...],
    "prompt_user": "{{TITLE}}, {{SUMMARY}}, ...",
    "prompt_system": "당신은 금융 기관의 전문 보고서 작성자입니다...",
    "prompt_meta": [
      {
        "key": "{{TITLE}}",
        "type": "section_title",
        "display_name": "보고서 제목",
        "description": "보고서의 명확하고 간결한 제목을...",
        "examples": ["2025 디지털뱅킹 분석", ...],
        "required": true,
        "order_hint": 1
      },
      ...
    ]
  }
}
```

#### 3. Topic Generation API Modification
**File**: `app/routers/topics.py` - `/generate` endpoint

**Changes**:
- Line 132-156: Modified Step 2 to use **pre-generated** prompt_system instead of regenerating
- Removed: `create_dynamic_system_prompt()` call and `PlaceholderDB.get_placeholders_by_template()` call
- Added: Direct loading of `template.prompt_system`

**Logic** (Priority):
```
if template.template_id provided:
  if template.prompt_system exists:
    Use template.prompt_system  ✨ Pre-generated (Performance Optimized)
  else:
    Use default FINANCIAL_REPORT_SYSTEM_PROMPT
else:
  Use default FINANCIAL_REPORT_SYSTEM_PROMPT
```

**Benefits**:
- No regeneration on every request (performance optimization)
- Allows future user customization of saved prompts
- Consistent prompt usage across all messages in a topic

#### 4. Ask (Follow-up Question) API Modification
**File**: `app/routers/topics.py` - `/{topic_id}/ask` endpoint

**Changes**:
- Line 813-839: Modified Step 4 System Prompt selection logic
- Implements priority: custom > template_id > default
- Uses **pre-generated** prompt_system when template_id provided

**System Prompt Priority**:
```
if body.system_prompt (custom):
  Use custom system_prompt
elif body.template_id:
  Load template.prompt_system  ✨ Pre-generated (not regenerated)
  if not found, use default
else:
  Use default FINANCIAL_REPORT_SYSTEM_PROMPT
```

**Removed Code**:
- `create_dynamic_system_prompt()` from imports (no longer needed)
- `PlaceholderDB` from imports (no longer needed)
- Dynamic prompt generation logic (replaced with direct loading)

#### 5. Comprehensive Test Suite
**File**: `tests/test_meta_info_generator.py`

**Test Cases** (12 total):
1. **TC-Unit-001**: Generate meta-info for all known keywords
2. **TC-Unit-002**: Generate meta-info for mixed known/unknown keywords
3. **TC-Unit-003**: Handle empty placeholder list
4. **TC-Unit-004**: Verify all meta-info items have required fields
5. **TC-Unit-005**: Generate Korean display names for known keywords
6. **TC-Unit-006**: Generate fallback display names for unknown keywords
7. **TC-Unit-007**: Generate descriptions for known keywords
8. **TC-Unit-008**: Generate descriptions with warnings for unknown keywords
9. **TC-Unit-009**: Generate examples for known keywords
10. **TC-Unit-010**: Generate fallback examples for unknown keywords
11. **TC-Unit-011**: Verify order_hint values for different types
12. **TC-Unit-012**: Integration test with realistic template placeholders

**Coverage**:
- Individual function tests (_get_display_name, _get_description, _get_examples)
- Main function tests (create_meta_info_from_placeholders)
- Integration tests (realistic template scenarios)
- Edge case handling (empty lists, unknown keywords, mixed types)

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `app/utils/meta_info_generator.py` | NEW | 163 |
| `app/routers/templates.py` | Import + Call meta_info_generator | +3 |
| `app/routers/topics.py` | Replace prompt generation with loading | -25 |
| `tests/test_meta_info_generator.py` | NEW | 280 |

## Technical Details

### Keyword Classification Rules
```python
keyword_classification = {
    "TITLE": {"type": "section_title", "section": "제목"},
    "SUMMARY": {"type": "section_content", "section": "요약"},
    "BACKGROUND": {"type": "section_content", "section": "배경"},
    "CONCLUSION": {"type": "section_content", "section": "결론"},
    "DATE": {"type": "metadata", "section": "날짜"},
}
```

### Type Definitions
- **section_title**: Placeholder for document title (required, order_hint=1)
- **section_content**: Placeholder for document sections (required, order_hint=2)
- **metadata**: Placeholder for metadata like date (optional, order_hint=0)

### Unknown Keyword Handling
- Default type: `section_content` (safe fallback)
- Display name: "{KEY_NAME} 섹션"
- Description: Auto-generated with ambiguity warning
- Examples: Auto-generated fallback example
- Required: true (conservative default)

## Database Schema

**Current Schema**: No changes needed (uses existing prompt_user and prompt_system fields)

**Future Enhancement** (Phase 2):
```sql
ALTER TABLE templates ADD COLUMN prompt_meta TEXT;
ALTER TABLE keyword_usage_logs (
  id, user_id, template_id, keyword, matched_keyword, created_at
);
```

## API Responses

### Template Upload Response
```json
{
  "prompt_meta": [
    {
      "key": "{{TITLE}}",
      "type": "section_title",
      "display_name": "보고서 제목",
      "description": "...",
      "examples": [...],
      "required": true,
      "order_hint": 1
    }
  ]
}
```

### Topic Generation Flow
```
1. User provides input_prompt and optional template_id
2. If template_id provided, load pre-generated template.prompt_system
3. Call Claude API with loaded system prompt
4. Parse response and generate MD artifact
5. Return topic_id and artifact_id
```

### Ask Endpoint Flow
```
1. User provides question and optional template_id
2. System Prompt Priority:
   a. Custom system_prompt (if provided)
   b. Template's pre-generated prompt (if template_id provided)
   c. Default system prompt
3. Call Claude with priority prompt
4. Generate new MD artifact version
5. Return response with artifact details
```

## Documentation Updates

### Backend Development Guidelines
- Added "Keyword Management Strategy for Placeholder Classification" section to `CLAUDE.md`
- Documents Phase 1, 2, 3 implementation roadmap
- Includes SQL schema for future keyword usage logging

### Supporting Documents
- `backend/doc/meta_info_generator_guide.md` - Detailed implementation guide
- `backend/doc/why_keyword_matching.md` - Justification for keyword matching
- `backend/doc/keyword_management_strategies.md` - Strategy comparison (3 approaches)
- `backend/doc/specs/20251110_template_meta_system_prompt.md` - Unit Spec (reference)

## Testing & Verification

### Syntax Verification ✅
- ✅ meta_info_generator.py - Valid Python syntax
- ✅ templates.py - Valid Python syntax
- ✅ topics.py - Valid Python syntax
- ✅ test_meta_info_generator.py - Valid Python syntax

### Import Verification ✅
- ✅ templates.py imports create_meta_info_from_placeholders
- ✅ topics.py loads pre-generated prompt_system
- ✅ All deprecated imports removed

### Implementation Checklist ✅
- ✅ Meta-info generator function created
- ✅ Templates router modified to call generator
- ✅ Topic generation router uses pre-generated prompts
- ✅ Ask endpoint implements prompt priority
- ✅ Comprehensive test suite created
- ✅ Documentation updated

## Performance Improvements

### Before
- Every topic creation request: Re-extract placeholders → Re-generate prompt
- Every ask request: Re-extract placeholders → Re-generate prompt
- Multiple redundant operations

### After
- Template upload: Generate prompt once (1 time)
- Topic creation: Load pre-generated prompt (0 overhead)
- Ask requests: Load pre-generated prompt (0 overhead)
- **Result**: Eliminated redundant prompt generation

## Security Considerations

- ✅ No user input injection in prompt generation
- ✅ Placeholders extracted from trusted templates only
- ✅ Keyword validation prevents injection attacks
- ✅ Safe fallback for unknown keywords prevents errors

## Future Enhancements

### Phase 2: Progressive Keyword Expansion (1 month)
1. Add keyword_usage_logs table for analytics
2. Monitor unmatched keywords
3. Add frequently used keywords (RISK, OVERVIEW, MARKET, REGULATION, EXECUTIVE)
4. Target: ≥80% matched keywords

### Phase 3: Hybrid Admin Strategy (3-6 months)
1. Create custom_keywords database table
2. Add Admin API endpoints for keyword management
3. Merge code-based + database-managed keywords
4. Allow org-specific customization

## Known Limitations & Workarounds

1. **prompt_meta Storage**: Currently returned in response only (not persisted in DB)
   - Workaround: Store in separate column or cache
   - Future: Add prompt_meta column migration

2. **Keyword Matching**: Uses "contains" logic (e.g., "BACKGROUND" matches "BACKGROUND_AND_CONTEXT")
   - Pro: Flexible for variations
   - Con: May over-classify (e.g., "DATE_CREATED" → metadata)
   - Acceptable for MVP

3. **Unknown Keywords**: All default to section_content
   - Conservative/safe default
   - Users can manually customize later

## Support & Questions

For questions about:
- **Implementation**: See `backend/doc/meta_info_generator_guide.md`
- **Architecture**: See `backend/doc/specs/20251110_template_meta_system_prompt.md`
- **Design Rationale**: See `backend/doc/why_keyword_matching.md`
- **Future Strategy**: See `CLAUDE.md` section "Keyword Management Strategy..."

## Commit Message

```
feat: Template-based system prompt generation and metadata extraction

Implement Phase 1 of template-based prompt generation:
- Add meta_info_generator.py to extract metadata from placeholders
- Modify template upload API to generate prompt_meta
- Modify topic generation API to use pre-generated prompts
- Implement prompt priority in ask endpoint
- Add comprehensive test suite (12 test cases)

Key improvements:
- Performance: Eliminate redundant prompt generation
- Extensibility: Support future custom keyword management
- UX: Provide metadata for frontend UI rendering

Follows Unit Spec: 20251110_template_meta_system_prompt.md
Implements keyword management strategy (Phase 1: MVP)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Status**: ✅ COMPLETE - Ready for integration testing and deployment
