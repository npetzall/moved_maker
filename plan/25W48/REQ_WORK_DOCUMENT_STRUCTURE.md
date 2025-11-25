# REQ: Work Document Structure

**Status**: ✅ Complete

## Overview

This request establishes a standardized structure for organizing work documents (requests, bugs, and implementation plans) using a year-week based work package system. This structure will be implemented together with the Cursor AI setup (see [CURSORRULES.md](CURSORRULES.md) and [CURSOR_AI_TEMPLATES.md](CURSOR_AI_TEMPLATES.md)) to ensure consistent documentation and AI-assisted workflow.

## Motivation

Currently, work documents are organized with sequential prefixes (`00_Initial`, `01_Quality`, `02_W47`, `03_W48`) and mixed document types. This structure has several issues:

- Sequential prefixes don't scale well and require renumbering
- No clear distinction between planning documents and implementation plans
- Inconsistent naming conventions across document types
- Difficult to track work by time period
- No clear backlog management

A year-week based structure with consistent prefixes will:
- Provide chronological organization that naturally sorts correctly
- Clearly separate planning documents from implementation plans
- Enable easy backlog management
- Support weekly work packages (sprints)
- Minimize file movement (files stay in their week directory)

## Current State

Current structure:
```
plan/
  ├── 00_Initial/
  ├── 01_Quality/
  ├── 02_W47/
  ├── 03_W48/
  └── XX_Backlog/

bugs/
  ├── 00_Initial/done/
  ├── 01_Quality/done/
  └── ...

work/
  ├── 00_Initial/
  ├── 01_Quality/
  └── 02_W47/
```

Issues:
- Mixed document types in `plan/` (some are requests, some are bugs, some are design docs)
- Sequential numbering requires maintenance
- `done/` folders add complexity
- No clear relationship between `plan/` and `work/` documents

## Proposed Structure

### Directory Organization

```
moved_maker/
├── plan/                    # Requests and bugs
│   ├── 24W47/               # Year + Week format (2-digit year, W, 2-digit week)
│   ├── 24W48/
│   ├── 24W49/
│   └── XX_Backlog/          # Unplanned items
│
└── work/                    # Implementation plans
    ├── 24W47/
    ├── 24W48/
    └── 24W49/
```

### Naming Convention

**Prefixes (only 2 types):**
- `REQ_` - Requests (from user, developer, architect, stakeholder, or product owner)
- `BUG_` - Bug reports

**File Naming Rules:**
1. **Identical filenames** between `plan/` and `work/` for all documents:
   - `plan/24W48/REQ_PULL_REQUEST_WORKFLOW.md`
   - `work/24W48/REQ_PULL_REQUEST_WORKFLOW.md`

2. **Both REQ and BUG** get implementation plans in `work/` folder

3. **No `done/` folders** - completed items stay in their week directory with status updated

### Status Tracking

Add a status header at the top of each document in `plan/`:

```markdown
# REQ: [Title]  (or # BUG: [Title])

**Status**: 📋 Planned | 🟡 In Progress | ✅ Complete | ⏸️ Blocked

## Overview
...
```

### Workflow

1. **Discovery** → Add to `plan/XX_Backlog/` with `REQ_` or `BUG_` prefix
2. **Planning** → Move to `plan/24W48/`, review and improve
3. **Implementation** → Create matching file in `work/24W48/` with same filename
4. **Completion** → Update status to "Complete" in `plan/` document (leave in place)

### Example Structure

```
plan/24W48/
├── REQ_PULL_REQUEST_WORKFLOW_SEQUENTIAL_CACHE.md
├── REQ_ALIGN_CRATE_AND_REPOSITORY.md
├── REQ_ROBUST_PR_LABELING.md
└── BUG_RELEASE_NOTES_NOT_FOUND.md

work/24W48/
├── REQ_PULL_REQUEST_WORKFLOW_SEQUENTIAL_CACHE.md
├── REQ_ALIGN_CRATE_AND_REPOSITORY.md
├── REQ_ROBUST_PR_LABELING.md
└── BUG_RELEASE_NOTES_NOT_FOUND.md

plan/XX_Backlog/
├── REQ_FUTURE_FEATURE.md
└── BUG_EDGE_CASE.md
```

## Integration with Cursor AI

This structure will work together with:

1. **`.cursorrules` files** (see [CURSORRULES.md](CURSORRULES.md)):
   - `plan/.cursorrules` will guide AI to use `REQ_` and `BUG_` prefixes
   - Document structure guidelines for requests and bugs

2. **Cursor AI Templates** (see [CURSOR_AI_TEMPLATES.md](CURSOR_AI_TEMPLATES.md)):
   - Templates will be updated to match `REQ_` and `BUG_` naming
   - Templates will include status header format
   - Templates will guide creation of matching files in `work/` folder

3. **DEVELOPMENT.md** (TODO - needs to be updated):
   - Add new section documenting Cursor AI setup and workflow
   - Add explanation of work document structure
   - Add guidelines for creating and organizing documents
   - Note: This should be done as part of the implementation

## Implementation Considerations

### Year-Week Format

- **Format**: `24W48` (2-digit year, W, 2-digit week)
- **ISO Week**: Use ISO week numbers (Monday as first day of week)
- **Leading zeros**: Use `24W01` not `24W1` for consistent sorting
- **Migration**: Map existing packages to actual weeks:
  - `00_Initial` → Determine actual week or use `24W00`
  - `01_Quality` → Determine actual week
  - `02_W47` → `24W47`
  - `03_W48` → `24W48`

### Document Migration

1. **Rename directories** from sequential to year-week format
2. **Rename files** to use `REQ_` or `BUG_` prefix:
   - Planning documents → `REQ_*.md`
   - Bug reports → `BUG_*.md`
3. **Add status headers** to all documents in `plan/`
4. **Create matching files** in `work/` for existing implementation plans
5. **Remove `done/` folders** and update status to "Complete" in documents

### Template Updates

Update Cursor AI templates to:
- Use `REQ_` prefix instead of `PLAN_` or `CHANGE_REQUEST_`
- Include status header format
- Reference the work document structure
- Guide creation of matching `work/` files

### .cursorrules Updates

Update `plan/.cursorrules` to:
- Specify `REQ_` and `BUG_` prefixes
- Document year-week directory naming
- Guide status header usage
- Reference relationship between `plan/` and `work/` folders

## Files to Modify/Create

### New Files
- `plan/25W48/REQ_WORK_DOCUMENT_STRUCTURE.md` (this file)
- `work/25W48/REQ_WORK_DOCUMENT_STRUCTURE.md` (implementation plan)
- `.cursor/templates/req_template.md` (updated from change_request.md)
- `.cursor/templates/bug_template.md` (updated from bug_report.md)

### Modified Files
- `plan/.cursorrules` - Add work document structure guidelines
- `.cursor/templates/implementation_plan_template.md` - Update to match new structure
- `DEVELOPMENT.md` - Add Cursor AI and work document structure section
- Root `.cursorrules` - Reference work document structure

### Directory Structure Changes
- Rename `plan/00_Initial/` → `plan/25W45/`
- Rename `plan/01_Quality/` → `plan/25W46/`
- Rename `plan/02_W47/` → `plan/25W47/`
- Rename `plan/03_W48/` → `plan/25W48/`
- Rename `work/00_Initial/` → `work/25W45/`
- Rename `work/01_Quality/` → `work/25W46/`
- Rename `work/02_W47/` → `work/25W47/`
- Remove `bugs/` directory (merge into `plan/`)
- Remove all `done/` subdirectories

## Testing Strategy

- **Verification**: Ensure all documents have correct prefixes and status headers
- **Consistency**: Verify filenames match between `plan/` and `work/` folders
- **Sorting**: Verify year-week directories sort correctly
- **Cursor AI**: Test that AI can generate documents following the new structure
- **Templates**: Verify templates produce correctly formatted documents

## Documentation Updates

- [ ] **Update `DEVELOPMENT.md`** - Add new section "Cursor AI Setup and Workflow" with:
  - Explanation of `.cursorrules` files and their hierarchy
  - Documentation of Cursor AI templates
  - Complete work document structure documentation (directory structure, naming conventions, status tracking, workflow)
  - Usage guidelines for Cursor AI
  - Cross-references to related documents (CURSORRULES.md, CURSOR_AI_TEMPLATES.md, this document)
- [ ] Update `plan/.cursorrules` with structure guidelines
- [ ] Update root `.cursorrules` to reference structure
- [ ] Update templates to match new naming convention

## Success Criteria

- [ ] All directories renamed to year-week format
- [ ] All documents use `REQ_` or `BUG_` prefix
- [ ] All documents have status headers
- [ ] Matching files exist in `plan/` and `work/` for all active items
- [ ] `bugs/` directory removed and merged into `plan/`
- [ ] All `done/` folders removed
- [ ] Cursor AI templates updated
- [ ] `.cursorrules` files updated
- [ ] `DEVELOPMENT.md` updated with Cursor AI section
- [ ] Structure documented and clear

## Related Documents

- [CURSORRULES.md](CURSORRULES.md) - Cursor AI rules setup
- [CURSOR_AI_TEMPLATES.md](CURSOR_AI_TEMPLATES.md) - Template creation and structure
- `DEVELOPMENT.md` - Will include Cursor AI and work document structure section

## Notes

- This should be implemented together with CURSORRULES.md and CURSOR_AI_TEMPLATES.md
- The year-week format provides natural chronological sorting
- No file movement needed after initial organization (files stay in their week directory)
- Status tracking replaces the need for `done/` folders
- Both REQ and BUG documents get implementation plans in `work/` folder
