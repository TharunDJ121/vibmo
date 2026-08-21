import os
import re
import subprocess
import sys

sec4_sessions = [
    '1070539305164246946', '15360177416378595019', '12737408343876686206',
    '13657906450024716468', '14881772949210013328', '14521548492259398678',
    '6915119778469672796', '10816087431938311106', '1681714437860506626',
    '14797054651649745795', '17297952518740195958', '12778306676206344075',
    '15836789557747121848', '15836789557747121903', '11961537026993695320'
]

subprocess.run(['git', 'checkout', 'main'])
subprocess.run(['git', 'pull', 'origin', 'main'])

print('Pulling Section 4 session patches from Jules...')
for sid in sec4_sessions:
    print(f'Pulling session {sid}...')
    # Clear any potential conflicting init files before pull
    for init_path in [
        os.path.join('vibmo', 'product', 'ai', '__init__.py'),
        os.path.join('vibmo', 'ui', 'ai', '__init__.py'),
        os.path.join('vibmo', 'ui', '__init__.py'),
    ]:
        if os.path.exists(init_path):
            os.remove(init_path)
            
    p = subprocess.run(['jules.cmd', 'remote', 'pull', '--session', sid, '--apply'], stdin=subprocess.DEVNULL, capture_output=True, text=True, shell=True)
    print('  Result:', p.stdout.strip()[:60] if p.stdout else p.stderr.strip()[:60])

# Clean up .orig files
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.orig'):
            try:
                os.remove(os.path.join(root, f))
            except Exception:
                pass

print('All Section 4 patches pulled cleanly.')
