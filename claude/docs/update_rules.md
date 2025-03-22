# Documentation Update Rules

This guide outlines the process for making documentation updates while maintaining system-wide consistency.

## General Principles

1. **Single Source of Truth**: Each piece of information should exist in exactly one canonical location.
2. **Complete Updates**: Changes must propagate to all affected documents.
3. **Consistency First**: Maintaining consistency takes priority over adding new content.
4. **Test Before Commit**: Validate all documentation changes before committing them.

## Documentation Change Workflow

### 1. Impact Assessment

Before making any documentation change:

- Identify the canonical document for the information being changed
- Search for all cross-references to the document being modified
- Determine which indexes include the document
- List all documents that might need corresponding updates

```bash
# Find all references to a specific pattern
grep -r "\[Pattern:ResourceManagement:1.0\]" --include="*.md" .

# Find all references to a file path
grep -r "/components/task-system/spec/types.md" --include="*.md" .
```

### 2. Cross-Reference Management

When updating documents with formal references:

- **Version Changes**: When making substantive changes, increment the version number in the reference ID
  - Major version (X.0) for breaking changes
  - Minor version (1.X) for additions
  - Patch version (1.1.X) for clarifications or fixes
  
- **Reference Updates**: Update all cross-references to reflect new versions
  - Example: Change `[Pattern:ResourceManagement:1.0]` to `[Pattern:ResourceManagement:1.1]` everywhere

- **Backwards Compatibility**: Maintain backwards compatibility notices for major version changes

### 3. Index Updates

When a document change affects an index:

- **ADR Index**: Update `/system/architecture/decisions/index.md`
  - Update status and completion percentages
  - Add new ADRs or update existing entries

- **Documentation Map**: Update `/system/docs-guide.md`
  - Add new documents to appropriate section
  - Update purpose or key content descriptions
  - Update any visual maps (Mermaid diagrams)

- **Component Indexes**: Update component README.md files
  - Add/update references to new or changed documents

### 4. Path Updates

When moving or renaming documents:

- Update all absolute path references (e.g., `/components/handler/README.md`)
- Update navigation paths in `/system/docs-guide.md`
- Add temporary redirects or compatibility notices when appropriate

### 5. Component-Specific Rules

#### System Architecture Documents

When updating pattern documents:
- Keep patterns conceptual and implementation-neutral
- Move implementation details to component impl directories
- Update all `[Implementation:X:Y.Z]` references

#### Component Documents

When updating component interfaces:
- Update the component's README.md
- Update any contracts in `/system/contracts/`
- Ensure type definitions remain consistent

#### Contract Documents

When updating contracts:
- Update all components that reference the contract
- Add compatibility notices for breaking changes
- Update XML schemas in `/system/contracts/protocols.md` if needed

### 6. Documentation Validation

After making changes:

1. **Reference Check**:
   ```bash
   # Check for broken references
   ./scripts/check-doc-refs.sh  # (If such a script exists)
   
   # Or manually check with grep for references that might be broken
   grep -r "\[Pattern:ResourceManagement:1.0\]" --include="*.md" .
   ```

2. **Path Check**:
   - Verify all internal links use the correct paths
   - Test navigation between documents

3. **Consistency Check**:
   - Ensure terminology is consistent across documents
   - Verify version numbers match across references
   - Confirm example code is consistent

## Special Cases

### ADR Updates

When creating or updating an ADR:
1. Update `/system/architecture/decisions/index.md`
2. Add cross-references to affected component docs
3. Update any superseded ADRs with pointers to the new ADR

### Interface Changes

When updating an interface:
1. Update all implementing components
2. Update all contract documents that reference the interface
3. Update example code in implementation documents

### Component Addition

When adding a new component:
1. Create standard directory structure with README.md, spec/, and impl/
2. Add to the documentation map in `/system/docs-guide.md`
3. Add cross-references to related system-level documents
4. Update any diagrams that show component relationships

## Documentation Debt Management

If unable to make all necessary updates at once:
1. Create a "Documentation Debt" issue tracking needed updates
2. Add a notice in affected documents indicating pending updates
3. Prioritize documentation debt resolution in future work

## Example Update Sequence

For adding a new behavior to a component:

1. Update the canonical spec document (e.g., `/components/handler/spec/behaviors.md`)
2. Update the component README.md to reference the new behavior
3. Update implementation docs with examples
4. Update the documentation map if adding new documents
5. Update any cross-references in system patterns
6. Validate all documentation changes
