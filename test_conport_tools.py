import os
import sys
import json

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(REPO_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from context_portal_mcp.db import models
from context_portal_mcp.handlers import mcp_handlers as H


def as_json(obj):
    try:
        return json.dumps(obj, indent=2, default=str)
    except TypeError:
        try:
            return json.dumps(obj.model_dump(mode="json"), indent=2, default=str)
        except Exception:
            return str(obj)


def get_id(obj):
    if isinstance(obj, dict):
        return obj.get("id")
    return getattr(obj, "id", None)


def main():
    workspace_id = os.getcwd()
    print(f"Workspace: {workspace_id}")

    print("--- Product Context ---")
    H.handle_update_product_context(models.UpdateContextArgs(workspace_id=workspace_id, content={"goal": "Test all the things!"}))
    pc = H.handle_get_product_context(models.GetContextArgs(workspace_id=workspace_id))
    print(as_json(pc))

    print("\n--- Active Context ---")
    H.handle_update_active_context(models.UpdateContextArgs(workspace_id=workspace_id, content={"focus": "Running test script."}))
    ac = H.handle_get_active_context(models.GetContextArgs(workspace_id=workspace_id))
    print(as_json(ac))

    print("\n--- Decision Logging ---")
    dec = H.handle_log_decision(models.LogDecisionArgs(workspace_id=workspace_id, summary="Script test decision", rationale="Automated test.", tags=["script", "test"]))
    decs = H.handle_get_decisions(models.GetDecisionsArgs(workspace_id=workspace_id, limit="1"))
    print(as_json(decs))

    print("\n--- Progress Logging ---")
    prog = H.handle_log_progress(models.LogProgressArgs(workspace_id=workspace_id, status="IN_PROGRESS", description="Running script tests"))
    progs = H.handle_get_progress(models.GetProgressArgs(workspace_id=workspace_id, limit="1"))
    print(as_json(progs))

    print("\n--- System Pattern Logging ---")
    patt = H.handle_log_system_pattern(models.LogSystemPatternArgs(workspace_id=workspace_id, name="Test Script Pattern", description="A pattern for testing.", tags=["script"]))
    patts = H.handle_get_system_patterns(models.GetSystemPatternsArgs(workspace_id=workspace_id, limit="1"))
    print(as_json(patts))

    print("\n--- Custom Data Logging ---")
    H.handle_log_custom_data(models.LogCustomDataArgs(workspace_id=workspace_id, category="TestScript", key="Run1", value={"status": "success"}))
    cdata = H.handle_get_custom_data(models.GetCustomDataArgs(workspace_id=workspace_id, category="TestScript"))
    print(as_json(cdata))

    print("\n--- Linking ---")
    dec_id = get_id(dec if dec else (decs[0] if isinstance(decs, list) and decs else None))
    prog_id = get_id(prog if prog else (progs[0] if isinstance(progs, list) and progs else None))
    if dec_id is not None and prog_id is not None:
        link = H.handle_link_conport_items(models.LinkConportItemsArgs(
            workspace_id=workspace_id,
            source_item_type="decision",
            source_item_id=str(dec_id),
            target_item_type="progress_entry",
            target_item_id=str(prog_id),
            relationship_type="tested_by"
        ))
        links = H.handle_get_linked_items(models.GetLinkedItemsArgs(workspace_id=workspace_id, item_type="decision", item_id=str(dec_id)))
        print(as_json(links))
    else:
        print("Skipping linking due to missing IDs")

    print("\n--- FTS ---")
    fts = H.handle_search_decisions_fts(models.SearchDecisionsArgs(workspace_id=workspace_id, query_term="script", limit="2"))
    print(as_json(fts))

    print("\n--- Project Glossary FTS ---")
    glossary = H.handle_search_project_glossary_fts(models.SearchProjectGlossaryArgs(workspace_id=workspace_id, query_term="script", limit=" 5 "))
    print(as_json(glossary))

    print("\n--- Recent Activity Summary ---")
    ras = H.handle_get_recent_activity_summary(models.GetRecentActivitySummaryArgs(workspace_id=workspace_id, hours_ago="24", limit_per_type="3"))
    print(as_json(ras))

    print("\n--- Export ---")
    export = H.handle_export_conport_to_markdown(models.ExportConportToMarkdownArgs(workspace_id=workspace_id))
    print(as_json(export))


if __name__ == "__main__":
    main()
