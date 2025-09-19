#!/usr/bin/env python3
"""
Test script to verify string-to-integer coercion fix in ConPort MCP tools.
This script tests the get_decisions tool with string limit parameter.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_mcp_tool_with_string_limit():
    """Test the get_decisions tool with a string limit parameter."""
    
    # Test payload for get_decisions with string limit
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_decisions",
            "arguments": {
                "workspace_id": "c:/Users/scott/Workspaces/context-portal",
                "limit": "3"  # This is a string, should be converted to int
            }
        }
    }
    
    print("Testing get_decisions with string limit='3'...")
    print(f"Test request: {json.dumps(test_request, indent=2)}")
    
    try:
        # Start the ConPort MCP server process
        process = subprocess.Popen(
            ["conport-mcp", "--mode", "stdio", "--workspace_id", "c:/Users/scott/Workspaces/context-portal"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Send the test request
        request_json = json.dumps(test_request)
        print(f"\nSending request: {request_json}")
        
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        print(f"\nStdout: {stdout}")
        print(f"Stderr: {stderr}")
        print(f"Return code: {process.returncode}")
        
        if stdout:
            try:
                response = json.loads(stdout)
                print(f"\nParsed response: {json.dumps(response, indent=2)}")
                
                if "error" in response:
                    print(f"❌ ERROR: {response['error']}")
                    return False
                else:
                    print("✅ SUCCESS: No error in response!")
                    return True
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                return False
        else:
            print("❌ No stdout received")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("=== ConPort String-to-Integer Coercion Test ===")
    success = test_mcp_tool_with_string_limit()
    
    if success:
        print("\n🎉 Test PASSED: String-to-integer coercion is working!")
        sys.exit(0)
    else:
        print("\n💥 Test FAILED: String-to-integer coercion is not working")
        sys.exit(1)