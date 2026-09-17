#!/usr/bin/env python3
import os
import re
from pathlib import Path

ROOT_DIR = Path('/Users/eshwarsaielugam/Documents/_/project-root')
ARCH_FILE = ROOT_DIR / 'docs' / 'architecture' / 'ARCHITECTURE.md'

def verify():
    with open(ARCH_FILE, 'r') as f:
        content = f.read()

    tree_text = content.split('```text')[1].split('```')[0].strip()
    
    current_path = []
    missing_paths = []
    
    for line in tree_text.split('\n'):
        if line.startswith('project-root/'):
            continue
            
        match = re.search(r'[a-zA-Z0-9_\-\.]', line)
        if not match:
            continue
            
        name_start_idx = match.start()
        depth = name_start_idx // 4
        
        name_part = line[name_start_idx:]
        name_part = name_part.split(' ')[0]
        
        current_path = current_path[:max(0, depth - 1)]
        
        if '{' in name_part:
            files = name_part.replace('{', '').replace('}', '').split(',')
            for file in files:
                full_path = os.path.join(*current_path, file.strip())
                if not (ROOT_DIR / full_path).exists():
                    missing_paths.append(full_path)
        else:
            full_path = os.path.join(*current_path, name_part)
            
            # For directories, the tree sometimes lists them without trailing slash in certain blocks, 
            # but usually with trailing slash. If it has trailing slash it's definitely a dir.
            if full_path.endswith('/'):
                check_path = full_path[:-1]
                if not (ROOT_DIR / check_path).exists():
                    missing_paths.append(full_path)
                current_path.append(name_part[:-1])
            else:
                if not (ROOT_DIR / full_path).exists():
                    missing_paths.append(full_path)
                    
    if missing_paths:
        print(f"FAILED: Found {len(missing_paths)} missing paths:")
        for p in missing_paths:
            print(f" - {p}")
        exit(1)
    else:
        print("SUCCESS: All paths from ARCHITECTURE.md exist.")
        exit(0)

if __name__ == '__main__':
    verify()
