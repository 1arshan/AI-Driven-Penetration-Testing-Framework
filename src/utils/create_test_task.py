#!/usr/bin/env python3
import requests
import json
import argparse
import time
import sys

def create_task(host='localhost', port=8000, token='dev_token'):
    """Create a test task and simulate progress updates"""
    base_url = f"http://{host}:{port}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create task
    task_data = {
        "type": "reconnaissance",
        "target": "192.168.1.1",
        "scope": {
            "ip_range": "192.168.1.0/24",
            "excluded_ips": [],
            "excluded_ports": [],
            "max_depth": 2
        },
        "description": "Test reconnaissance task",
        "priority": 2
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/task/create",
            headers=headers,
            json=task_data
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result["task_id"]
            print(f"Created task with ID: {task_id}")
            
            # Simulate task status updates
            for progress in [10, 25, 50, 75, 100]:
                time.sleep(2)  # Wait 2 seconds between updates
                
                status = "completed" if progress == 100 else "in_progress"
                message = "Task completed successfully" if progress == 100 else f"Processing task: {progress}% complete"
                
                status_url = f"{base_url}/api/task/{task_id}/status"
                status_data = {
                    "status": status,
                    "progress": float(progress),
                    "message": message
                }
                
                status_response = requests.put(
                    status_url,
                    headers=headers,
                    json=status_data
                )
                
                if status_response.status_code == 200:
                    print(f"Updated task status: {progress}% complete")
                else:
                    print(f"Failed to update task status: {status_response.status_code}")
                    print(status_response.text)
            
            print("Task simulation completed")
            return task_id
        else:
            print(f"Failed to create task: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a test task and simulate progress updates")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--token", default="dev_token", help="Authentication token")
    
    args = parser.parse_args()
    
    create_task(args.host, args.port, args.token)