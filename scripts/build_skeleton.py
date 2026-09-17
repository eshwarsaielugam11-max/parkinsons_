#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Paths
ROOT_DIR = Path('/Users/eshwarsaielugam/Documents/_/project-root')
ARCH_FILE = ROOT_DIR / 'docs' / 'architecture' / 'ARCHITECTURE.md'

# We don't touch these since they exist or are managed elsewhere
DO_NOT_TOUCH = ['model', '.git', 'scripts/sync_model_artifacts.sh', 'docs/architecture/ARCHITECTURE.md']

def parse_arch_doc():
    with open(ARCH_FILE, 'r') as f:
        content = f.read()

    # Parse View B to get Phase mappings
    view_b = content.split('## VIEW B: File-by-File Responsibility Map')[1]
    
    phase_map = {}
    for line in view_b.split('\n'):
        if line.startswith('| `') or line.startswith('| **'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 6:
                filepath = parts[1].replace('`', '')
                created_phase = parts[6]
                
                # Handle wildcards like backend/models/*.py -> just map backend/models
                if '*' in filepath:
                    base = filepath.split('*.')[0]
                    phase_map[base] = created_phase
                elif '{' in filepath:
                    # e.g., backend/api/{upload.py, stream.py}
                    dir_path = filepath.split('{')[0]
                    files = filepath.split('{')[1].split('}')[0].split(',')
                    for file in files:
                        phase_map[dir_path + file.strip()] = created_phase
                else:
                    phase_map[filepath] = created_phase

    # Extract tree lines
    tree_text = content.split('```text')[1].split('```')[0].strip()
    
    current_path = []
    
    paths_to_create = []
    
    for line in tree_text.split('\n'):
        if line.startswith('project-root/'):
            continue
            
        # Count indents: Each indent level in the tree is typically 4 spaces "│   " or "    "
        # We can just count the position of the first word character
        match = re.search(r'[a-zA-Z0-9_\-\.]', line)
        if not match:
            continue
            
        name_start_idx = match.start()
        
        # Determine depth based on name_start_idx
        # ├── is at 0
        # │   ├── is at 4
        # │   │   ├── is at 8
        depth = name_start_idx // 4
        
        # Clean the name
        name_part = line[name_start_idx:]
        name_part = name_part.split(' ')[0] # Remove trailing comments
        
        # Update current path stack
        current_path = current_path[:max(0, depth - 1)]
        
        if '{' in name_part:
            # It's a list of files e.g. {resample.py, vad.py}
            files = name_part.replace('{', '').replace('}', '').split(',')
            for file in files:
                full_path = os.path.join(*current_path, file.strip())
                paths_to_create.append(full_path)
        else:
            full_path = os.path.join(*current_path, name_part)
            paths_to_create.append(full_path)
            
            if name_part.endswith('/'):
                current_path.append(name_part[:-1])
                
    return paths_to_create, phase_map

def find_phase(filepath, phase_map):
    if filepath in phase_map:
        return phase_map[filepath]
        
    # Check for wildcard matches
    for key in phase_map:
        if filepath.startswith(key):
            return phase_map[key]
            
    return "Phase XX"

def create_skeleton():
    paths, phase_map = parse_arch_doc()
    
    for p in paths:
        if any(p.startswith(d) for d in DO_NOT_TOUCH):
            continue
            
        full_p = ROOT_DIR / p
        
        if p.endswith('/'):
            full_p.mkdir(parents=True, exist_ok=True)
        else:
            full_p.parent.mkdir(parents=True, exist_ok=True)
            if not full_p.exists():
                phase = find_phase(p, phase_map)
                
                # Determine content
                content = ""
                if p.endswith('.py'):
                    content = f'\"\"\"Module {full_p.name}.\"\"\"\n# TODO: implemented in {phase}\n'
                elif p.endswith('.ts') or p.endswith('.tsx'):
                    content = f'// Module {full_p.name}\n// TODO: implemented in {phase}\n'
                elif p.endswith('.json'):
                    content = "{}\n"
                elif p.endswith('.yaml') or p.endswith('.yml'):
                    content = f'# Configuration for {full_p.name}\n# TODO: implemented in {phase}\n'
                elif p.endswith('README.md'):
                    content = f'# {full_p.parent.name}\n\nThis directory contains components for {full_p.parent.name}. Implemented during {phase}.\n'
                elif p.endswith('.md'):
                    content = f'# {full_p.name}\n\nTODO: Documentation implemented in {phase}.\n'
                elif p.endswith('.sh'):
                    content = f'#!/usr/bin/env bash\n# TODO: implemented in {phase}\n'
                
                with open(full_p, 'w') as f:
                    f.write(content)
                    
                if p.endswith('.sh'):
                    os.chmod(full_p, 0o755)

if __name__ == '__main__':
    create_skeleton()
    print("Skeleton creation complete.")
