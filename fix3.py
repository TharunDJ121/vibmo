with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'r') as f:
    content = f.read()

content = content.replace('''    def decrypt(self, duration: float = 2.0) -> AnimationAction:
        """Starts the decryption animation from left to right."""
        # We also reset state if called multiple times
        self._last_locked_index = -1
        for cycle in self.cycles:
            cycle.progress.set(0.0)
        for flash in self.flashes:
            flash.flash_progress.set(0.0)

        return self.decrypt_progress.to(1.0, duration=duration, ease=Ease.linear)''', '''    def decrypt(self, duration: float = 2.0):
        """Starts the decryption animation from left to right."""
        # We also reset state if called multiple times
        self._last_locked_index = -1
        for cycle in self.cycles:
            cycle.progress.set(0.0)
        for flash in self.flashes:
            flash.flash_progress.set(0.0)

        yield self.decrypt_progress.to(1.0, duration=duration, ease=Ease.linear)''')

with open('vibmo/typography/kinetic/typo_glitch_decryptor_suite.py', 'w') as f:
    f.write(content)
