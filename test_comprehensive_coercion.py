#!/usr/bin/env python3
"""
Comprehensive test for string-to-integer coercion across multiple ConPort MCP tools.
Tests various tools that accept integer parameters as strings.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def send_mcp_request(process, request):
    """Send an MCP request and get response."""
    request_json = json.dumps(request) + "\n"
    print(f"Sending: {request['method']} with args: {request.get('params', {}).get('arguments', {})}")
    
    process.stdin.write(request_json)
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    
    if response_line:
        try:
            response = json.loads(response_line)
            if "error" in response:
                print(f"❌ Error: {response['error']['message']}")
                return False, response
            else:
                print("✅ Success!")
                return True, response
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse response: {e}")
            return False, None
    return False, None

def initialize_mcp(process):
    """Initialize MCP connection."""
    print("=== MCP Initialization ===")
    
    # Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "comprehensive-test-client",
                "version": "1.0.0"
            }
        }
    }
    
    success, response = send_mcp_request(process, init_request)
    if not success:
        return False
    
    # Send initialized notification
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    
    process.stdin.write(json.dumps(initialized_notification) + "\n")
    process.stdin.flush()
    print("✅ MCP initialized")
    
    # Wait for server to be ready
    time.sleep(1)
    return True

def test_comprehensive_coercion():
    """Test string-to-integer coercion across multiple tools."""
    
    workspace_id = "c:/Users/scott/Workspaces/context-portal"
    
    # Test cases: (tool_name, test_args, description)
    test_cases = [
        ("get_decisions", {"workspace_id": workspace_id, "limit": "5"}, 
         "get_decisions with string limit"),
        
        ("search_decisions_fts", {"workspace_id": workspace_id, "query_term": "test", "limit": "2"}, 
         "search_decisions_fts with string limit"),
        
        ("get_progress", {"workspace_id": workspace_id, "limit": "3"}, 
         "get_progress with string limit"),
        
        ("get_system_patterns", {"workspace_id": workspace_id, "limit": "4"}, 
         "get_system_patterns with string limit"),
        
        ("search_custom_data_value_fts", {"workspace_id": workspace_id, "query_term": "test", "limit": "1"}, 
         "search_custom_data_value_fts with string limit"),
        
        ("get_recent_activity_summary", {"workspace_id": workspace_id, "hours_ago": "24", "limit_per_type": "2"}, 
         "get_recent_activity_summary with string hours_ago and limit_per_type"),
        
        ("semantic_search_conport", {"workspace_id": workspace_id, "query_text": "test decision", "top_k": "3"}, 
         "semantic_search_conport with string top_k"),
    ]
    
    try:
        # Start the ConPort MCP server process
        process = subprocess.Popen(
            ["conport-mcp", "--mode", "stdio", "--workspace_id", workspace_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        if not initialize_mcp(process):
            print("❌ Failed to initialize MCP")
            return False
        
        print("\n=== Testing String-to-Integer Coercion Across Tools ===")
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, (tool_name, args, description) in enumerate(test_cases, 1):
            print(f"\n{i}/{total_tests}. Testing: {description}")
            
            test_request = {
                "jsonrpc": "2.0",
                "id": i + 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args
                }
            }
            
            success, response = send_mcp_request(process, test_request)
            if success:
                success_count += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print(f"\n=== Test Results ===")
        print(f"Passed: {success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("🎉 All tests PASSED! String-to-integer coercion is working across all tools!")
            return True
        else:
            print(f"💥 {total_tests - success_count} tests FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)

if __name__ == "__main__":
    print("=== ConPort Comprehensive String-to-Integer Coercion Test ===")
    success = test_comprehensive_coercion()
    
    if success:
        print("\n🎉 ALL TESTS PASSED: String-to-integer coercion is working comprehensively!")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED: Issues remain with string-to-integer coercion")
        sys.exit(1)