#!/usr/bin/env python3
"""Update Pydantic v1 Config classes to v2 model_config."""

import os
import re

def update_config_classes(file_path):
    """Update Config classes in a Python file to Pydantic v2 syntax."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match Config class with from_attributes
    pattern = r'class Config:\s+from_attributes = True'
    replacement = 'model_config = {\n        "from_attributes": True\n    }'
    
    # Replace simple Config classes
    updated = re.sub(pattern, replacement, content)
    
    # Pattern for Config class with json_schema_extra
    pattern2 = r'class Config:\s+from_attributes = True\s+json_schema_extra = \{'
    replacement2 = 'model_config = {\n        "from_attributes": True,\n        "json_schema_extra": {'
    
    updated = re.sub(pattern2, replacement2, updated)
    
    # Save if changed
    if updated != content:
        with open(file_path, 'w') as f:
            f.write(updated)
        print(f"Updated: {file_path}")
        return True
    return False

# Update all view files
views_dir = "app/views"
for filename in os.listdir(views_dir):
    if filename.endswith(".py"):
        file_path = os.path.join(views_dir, filename)
        update_config_classes(file_path)

print("Pydantic v2 migration completed!")