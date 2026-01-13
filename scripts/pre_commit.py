#!/usr/bin/env python3
import sys
import os
import subprocess

def bump_version(version_str):
    parts = version_str.strip().split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
    return '.'.join(parts)

def update_repo():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    version_file = os.path.join(repo_dir, "VERSION")
    history_file = os.path.join(repo_dir, "COMMIT_HISTORY.md")

    # 1. Bump VERSION
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            current_v = f.read().strip()
        new_v = bump_version(current_v)
        with open(version_file, 'w') as f:
            f.write(new_v + '\n')
        print(f"Bumped version: {current_v} -> {new_v}")
        subprocess.run(["git", "add", "VERSION"], cwd=repo_dir)

    # 2. Update COMMIT_HISTORY.md
    with open(history_file, 'w') as f:
        subprocess.run(["git", "log", "--oneline"], stdout=f, cwd=repo_dir)
    print("Updated COMMIT_HISTORY.md")
    subprocess.run(["git", "add", "COMMIT_HISTORY.md"], cwd=repo_dir)

    # 3. Update Site Dashboard if available
    base_dir = os.path.dirname(repo_dir)
    site_script = os.path.join(base_dir, "forgotten-future-site/scripts/pre_commit.py")
    if os.path.exists(site_script):
        print("Triggering site dashboard update...")
        subprocess.run(["python3", site_script, "--only-dashboard"])

if __name__ == "__main__":
    update_repo()
