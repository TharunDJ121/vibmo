with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'r') as f:
    content = f.read()

content = content.replace('if prog >= char_prog_end:', '''char_prog_end = (i + 1) / total_chars

            if prog >= char_prog_end:''')

with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'w') as f:
    f.write(content)
