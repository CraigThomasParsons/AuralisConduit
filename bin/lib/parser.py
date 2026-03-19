import re
import os

def parse_response(text: str):
    """
    Parses the LLM response text for file blocks.
    Format:
    ===FILE: path/to/file===
    content
    ===END===
    """
    files = [] # Kept for backward compat or just return list of actions
    actions = []
    
    # Regex to find blocks (FILE or RUN)
    # Group 1: Type (FILE|RUN)
    # Group 2: Argument (filename or language)
    # Group 3: Content
    pattern = re.compile(r"===(FILE|RUN): ([^\s=]+)===\s*(.*?)\s*===END===", re.DOTALL)
    
    matches = pattern.finditer(text)
    for match in matches:
        block_type = match.group(1).lower() # file or run
        argument = match.group(2).strip()
        content = match.group(3)
        
        if content.startswith("\n"):
            content = content[1:]
        if content.endswith("\n"):
            content = content[:-1]
            
        action = {
            "type": block_type,
            "content": content
        }
        
        if block_type == "file":
            action["path"] = argument
        elif block_type == "run":
            action["language"] = argument
            
        actions.append(action)
        
    return actions

def validate_path(repo_root: str, file_path: str):
    """
    Ensures file_path is safe to write (within repo_root/scratchpad by default).
    """
    # Normalize
    abs_root = os.path.abspath(repo_root)
    target_path = os.path.abspath(os.path.join(abs_root, "scratchpad", file_path))
    
    # Check escape
    if not target_path.startswith(abs_root):
        raise ValueError(f"Path traversal detected: {file_path}")
        
    return target_path
