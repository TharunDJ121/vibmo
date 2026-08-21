import os
import re
import subprocess
import sys

sec3_sessions = [
    '356092162934640875', '3974961576779090548', '14741906868268055869',
    '3596203027239485063', '3568014128124525307', '6473807493734465638',
    '6280175133218902586', '5968533270130597395', '7830556046867178348',
    '6772749611748507484', '16947262065571885821', '3471150045231689675',
    '9886631735756642294', '13828356173083707392', '4477752160660275497'
]

subprocess.run(['git', 'checkout', 'main'])
subprocess.run(['git', 'pull', 'origin', 'main'])

print('Pulling Section 3 session patches...')
for sid in sec3_sessions:
    print(f'Pulling session {sid}...')
    init_f = os.path.join('vibmo', 'product', 'hardware', '__init__.py')
    if os.path.exists(init_f):
        os.remove(init_f)
    p = subprocess.run(['jules.cmd', 'remote', 'pull', '--session', sid, '--apply'], stdin=subprocess.DEVNULL, capture_output=True, text=True, shell=True)
    print('  Result:', p.stdout.strip()[:60] if p.stdout else p.stderr.strip()[:60])

# Generate clean __init__.py for hardware
hw_dir = os.path.join('vibmo', 'product', 'hardware')
if os.path.exists(hw_dir):
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

print('Updated hardware __init__.py cleanly.')
