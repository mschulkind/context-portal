#!/usr/bin/env python3
"""
Proper MCP protocol test for string-to-integer coercion fix.
This script follows the MCP initialization sequence before testing tools.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def send_mcp_request(process, request):
    """Send an MCP request and get response."""
    request_json = json.dumps(request) + "\n"
    print(f"Sending: {request_json.strip()}")
    
    process.stdin.write(request_json)
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    print(f"Received: {response_line.strip()}")
    
    if response_line:
        try:
            return json.loads(response_line)
        except json.JSONDecodeError as e:
            print(f"Failed to parse response: {e}")
            return None
    return None

def test_mcp_with_proper_protocol():
    """Test MCP with proper initialization sequence."""
    
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
        
        print("=== MCP Initialization ===")
        
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_mcp_request(process, init_request)
        if not response or "error" in response:
            print(f"❌ Initialization failed: {response}")
            return False
        
        print("✅ Initialization successful")
        
        # Step 2: Initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        print("✅ Sent initialized notification")
        
        # Wait a moment for server to be ready
        time.sleep(1)
        
        print("\n=== Testing String-to-Integer Coercion ===")
        
        # Step 3: Test get_decisions with string limit
        test_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_decisions",
                "arguments": {
                    "workspace_id": "c:/Users/scott/Workspaces/context-portal",
                    "limit": "3"  # This is a string, should be converted to int
                }
            }
        }
        
        response = send_mcp_request(process, test_request)
        
        if response and "error" in response:
            print(f"❌ Tool call failed: {response['error']}")
            return False
        elif response and "result" in response:
            print("✅ Tool call successful!")
            print(f"Result: {json.dumps(response['result'], indent=2)}")
            return True
        else:
            print(f"❌ Unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)

if __name__ == "__main__":
    print("=== ConPort MCP Protocol Test ===")
    success = test_mcp_with_proper_protocol()
    
    if success:
        print("\n🎉 Test PASSED: String-to-integer coercion is working!")
        sys.exit(0)
    else:
        print("\n💥 Test FAILED: String-to-integer coercion is not working")
        sys.exit(1)