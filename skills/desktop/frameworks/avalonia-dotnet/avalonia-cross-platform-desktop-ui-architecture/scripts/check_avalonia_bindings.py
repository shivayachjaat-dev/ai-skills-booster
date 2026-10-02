#!/usr/bin/env python3
import os
import re
import sys

def audit_axaml(project_dir="."):
    print("=" * 65)
    print(f"Auditing Avalonia AXAML Compiled Bindings in: {project_dir}")
    print("=" * 65)

    axaml_files = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith(('.axaml', '.xaml')):
                axaml_files.append(os.path.join(root, f))

    if not axaml_files:
        print("No AXAML files found to audit.")
        return

    missing_datatype = []
    for path in axaml_files:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "x:DataType" not in content and "DataType=" not in content:
                missing_datatype.append(path)

    print(f"Total AXAML Files Inspected: {len(axaml_files)}")
    if missing_datatype:
        print(f"\n[WARNING]: {len(missing_datatype)} files lack compiled x:DataType bindings:")
        for p in missing_datatype:
            print(f"  - {os.path.relpath(p, project_dir)}")
        print("\nRecommendation: Add x:DataType to root controls for compile-time safety.")
    else:
        print("SUCCESS: All AXAML files declare explicit compiled binding types.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_axaml(target)
