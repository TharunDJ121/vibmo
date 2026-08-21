import os
import glob
import re
import subprocess
import sys

# Remove .orig files
for orig in glob.glob('vibmo/**/*.orig', recursive=True) + glob.glob('tests/**/*.orig', recursive=True):
    try:
        os.remove(orig)
        print('Removed:', orig)
    except Exception:
        pass

# Generate vibmo/product/hardware/__init__.py
hw_dir = os.path.join('vibmo', 'product', 'hardware')
hw_files = sorted([f for f in os.listdir(hw_dir) if f.startswith('hw_') and f.endswith('.py')])
imports = []
all_exports = []
for f in hw_files:
    mod = f[:-3]
    with open(os.path.join(hw_dir, f), 'r', encoding='utf-8', errors='ignore') as fh:
        classes = re.findall(r'^class\s+([A-Za-z0-9_]+)\s*\(', fh.read(), re.MULTILINE)
    if classes:
        imports.append(f'from vibmo.product.hardware.{mod} import (\n    ' + ',\n    '.join(classes) + ',\n)')
        all_exports.extend(classes)

init_code = '"""Hardware chassis and device enclosure suites."""\nfrom __future__ import annotations\n\n'
init_code += '\n'.join(imports) + '\n\n__all__ = [\n    ' + ',\n    '.join(f'"{c}"' for c in all_exports) + ',\n]\n'
with open(os.path.join(hw_dir, '__init__.py'), 'w', encoding='utf-8') as fh:
    fh.write(init_code)

print(f'Generated hardware __init__.py with {len(all_exports)} classes.')
