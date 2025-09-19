# Context Portal MCP v0.3.4 Release Notes

## 🚀 Version 0.3.4 - String-to-Integer Coercion Fix

**Release Date:** January 18, 2025

### 🐛 Bug Fixes

#### **Critical Fix: String-to-Integer Parameter Coercion**

**Problem:** ConPort MCP tools were failing when integer parameters (like `limit`, `hours_ago`, `top_k`, etc.) were passed as strings instead of native integers. This was causing "Unable to apply constraint 'ge' to supplied value" errors across multiple tools.

**Root Cause:** The issue was identified in two layers:
1. **FastMCP Tool Definitions:** Field-level Pydantic constraints (`ge=1`, `le=25`) in tool parameter annotations were being applied before the custom `IntCoercionMixin` could convert strings to integers.
2. **Pydantic Model Validation:** The validation order in Pydantic models was applying field-level constraints before the string-to-integer coercion process.

**Solution:** 
- **Removed all field-level `ge=` constraints** from FastMCP tool parameter definitions in `main.py`
- **Refactored Pydantic model validation** to use `@model_validator(mode='after')` instead of field-level constraints, ensuring validation occurs after successful type coercion
- **Enhanced `IntCoercionMixin`** to work seamlessly with post-validation checks

### 🔧 Technical Changes

#### Files Modified:
- **`src/context_portal_mcp/main.py`**: Removed `ge=1` and `le=25` constraints from 13 tool parameter definitions
- **`src/context_portal_mcp/db/models.py`**: Complete rewrite of validation approach using post-validation model validators

#### Tools Fixed:
All tools with integer parameters now properly support string-to-integer coercion:
- `get_decisions` (limit)
- `search_decisions_fts` (limit)
- `get_progress` (limit, parent_id_filter)
- `update_progress` (progress_id)
- `delete_progress_by_id` (progress_id)
- `get_system_patterns` (limit)
- `search_project_glossary_fts` (limit)
- `get_linked_items` (limit)
- `search_custom_data_value_fts` (limit)
- `get_item_history` (limit, version)
- `delete_decision_by_id` (decision_id)
- `delete_system_pattern_by_id` (pattern_id)
- `get_recent_activity_summary` (hours_ago, limit_per_type)
- `semantic_search_conport` (top_k)

### ✅ Testing

**Comprehensive Testing:** Created extensive test suite to verify the fix:
- **`test_mcp_protocol.py`**: Proper MCP protocol initialization and single tool testing
- **`test_comprehensive_coercion.py`**: Tests 7 different tools with string integer parameters
- **All tests passed**: 7/7 tools successfully handle string-to-integer coercion

### 🎯 Impact

**Before v0.3.4:**
```json
{
  "error": {
    "code": -32602,
    "message": "Unable to apply constraint 'ge' to supplied value 3"
  }
}
```

**After v0.3.4:**
```json
{
  "result": {
    "content": [
      // Successfully returns data with limit: "3" converted to 3
    ]
  }
}
```

### 🔄 Backward Compatibility

- ✅ **Fully backward compatible** - existing integer parameters continue to work
- ✅ **Enhanced flexibility** - now accepts both integer and string representations
- ✅ **Validation preserved** - all business logic constraints remain intact

### 📋 Upgrade Instructions

1. **For PyPI users:**
   ```bash
   pip install --upgrade context-portal-mcp
   ```

2. **For uvx users:**
   ```bash
   uvx --from context-portal-mcp@0.3.4 conport-mcp --version
   ```

3. **No configuration changes required** - the fix is transparent to end users

### 🔍 Technical Details

The fix ensures that string parameters like `"5"`, `"24"`, `"10"` are automatically converted to integers `5`, `24`, `10` before validation, while maintaining all existing validation rules (minimum values, maximum values, etc.).

**Example working calls:**
```python
# All of these now work seamlessly:
get_decisions(workspace_id="...", limit="5")      # string
get_decisions(workspace_id="...", limit=5)        # integer
semantic_search_conport(workspace_id="...", top_k="3")  # string top_k
get_recent_activity_summary(hours_ago="24")       # string hours_ago
```

---

**Full Changelog:** See [GitHub Releases](https://github.com/GreatScottyMac/context-portal/releases/tag/v0.3.4)