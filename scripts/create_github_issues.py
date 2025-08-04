#!/usr/bin/env python3
"""
Create GitHub issues from markdown files
"""

import os
import sys
import json
import subprocess
from pathlib import Path

ISSUES_DIR = Path(__file__).parent.parent / "docs" / "github_issues"

def extract_issue_info(md_file):
    """Extract title and body from markdown file"""
    with open(md_file, 'r') as f:
        lines = f.readlines()
    
    # First line after # is the title
    title = None
    for line in lines:
        if line.startswith("# Issue: "):
            title = line.replace("# Issue: ", "").strip()
            break
        elif line.startswith("# "):
            title = line.replace("# ", "").strip()
            break
    
    # Rest is body
    body = ''.join(lines[1:])
    
    # Extract labels from the file
    labels = []
    for line in lines:
        if line.strip().startswith("- ") and "## Labels" in ''.join(lines[max(0, lines.index(line)-5):lines.index(line)]):
            label = line.strip()[2:].strip()
            labels.append(label)
    
    return title, body, labels

def create_github_issue(title, body, labels):
    """Create a GitHub issue using gh CLI"""
    cmd = ["gh", "issue", "create", 
           "--title", title,
           "--body", body,
           "--repo", "toddllm/luanti-voyager"]
    
    # Add labels (only if they exist)
    # For now, skip labels as they need to be created first
    # for label in labels:
    #     cmd.extend(["--label", label])
    
    print(f"Creating issue: {title}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("GitHub Issue Creator")
    print("===================")
    print()
    
    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except:
        print("❌ Error: GitHub CLI (gh) not found!")
        print("Install with: https://cli.github.com/")
        sys.exit(1)
    
    # Check if authenticated
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: Not authenticated with GitHub!")
            print("Run: gh auth login")
            sys.exit(1)
    except:
        pass
    
    # Find all issue files
    issue_files = sorted(ISSUES_DIR.glob("issue_*.md"))
    
    if not issue_files:
        print("No issue files found in docs/github_issues/")
        sys.exit(1)
    
    print(f"Found {len(issue_files)} issue files")
    print()
    
    # Show what will be created
    issues = []
    for f in issue_files:
        title, body, labels = extract_issue_info(f)
        issues.append((f, title, body, labels))
        print(f"📄 {f.name}")
        print(f"   Title: {title}")
        print(f"   Labels: {', '.join(labels)}")
        print()
    
    # Confirm
    response = input("Create these issues? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    print()
    
    # Create issues
    created = []
    for f, title, body, labels in issues:
        url = create_github_issue(title, body, labels)
        if url:
            created.append((f.name, url))
    
    print()
    print(f"Created {len(created)} issues:")
    for name, url in created:
        print(f"  {name} -> {url}")

if __name__ == "__main__":
    main()