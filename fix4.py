with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'r') as f:
    content = f.read()

content = content.replace('''            char_prog_start = i / total_chars

            if prog >= char_prog_end:
                # This character is locked in''', '''            char_prog_start = i / total_chars
            char_prog_end = (i + 1) / total_chars

            if prog >= char_prog_end:
                # This character is locked in''')

with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'w') as f:
    f.write(content)
