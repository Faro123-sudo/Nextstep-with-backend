#!/usr/bin/env python3
"""
Test script for the AI Career Search API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/accounts/login/"
SEARCH_URL = f"{BASE_URL}/api/ai/search/"

def get_auth_token(username, password):
    """Get JWT token for authentication"""
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None
    data = response.json()
    return data.get("access")

def test_search(query, user_type="student", auth_token=None):
    """Test the career search endpoint"""
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "userType": user_type
    }
    
    response = requests.post(SEARCH_URL, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

if __name__ == "__main__":
    # You'll need to provide username and password
    if len(sys.argv) < 4:
        print("Usage: python test_search.py <username> <password> <query> [user_type]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    query = sys.argv[3]
    user_type = sys.argv[4] if len(sys.argv) > 4 else "student"
    
    print(f"Getting token for {username}...")
    token = get_auth_token(username, password)
    
    if not token:
        print("Failed to get auth token")
        sys.exit(1)
    
    print(f"Testing search for: '{query}'")
    test_search(query, user_type, token)