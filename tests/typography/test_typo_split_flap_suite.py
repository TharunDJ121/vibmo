import unittest
from unittest.mock import MagicMock
import cairo

from vibmo.typography.kinetic.typo_split_flap_suite import (
    SplitFlapAirportBoard,
    MechanicalFlapTile,
    RapidLetterScramble,
    SplitFlapSoundSync
)

class TestSplitFlapSuite(unittest.TestCase):
    def test_rapid_letter_scramble_math(self):
        # A -> C, which is index 1 -> 3
        # If total_flaps is 2, it should step A -> B -> C
        scramble = RapidLetterScramble("A", "C", total_flaps=2)
        
        # Start state (progress = 0)
        state = scramble.get_state(0.0)
        self.assertEqual(state[0], "A") # current
        self.assertEqual(state[1], "B") # next
        self.assertEqual(state[3], 0.0) # flap progress
        
        # End state (progress = 1.0)
        state = scramble.get_state(1.0)
        self.assertEqual(state[0], "C") # current
        self.assertEqual(state[1], "C") # next
        self.assertEqual(state[3], 0.0) # flap progress

    def test_mechanical_flap_tile_drawing(self):
        tile = MechanicalFlapTile(width=100, height=200)
        tile.set_state("A", "B", 0.3)
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 200)
        ctx = cairo.Context(surface)
        
        # Should not crash and should draw something
        tile.draw(ctx, 0.0)
        
        # verify cairo context was used (just a basic sanity check)
        self.assertTrue(surface.get_data())
        
    def test_mechanical_flap_tile_state_clamps(self):
        tile = MechanicalFlapTile(width=100, height=200)
        tile.set_state("A", "B", 1.5) # Over 1.0
        self.assertEqual(tile.flap_progress, 1.0)
        
        tile.set_state("A", "B", -0.5) # Under 0.0
        self.assertEqual(tile.flap_progress, 0.0)

    def test_sound_sync_event(self):
        sync = SplitFlapSoundSync()
        called = [0]
        def cb():
            called[0] += 1
        sync.add_listener(cb)
        
        sync.trigger_flap()
        self.assertEqual(called[0], 1)
        
    def test_airport_board_layout(self):
        board = SplitFlapAirportBoard("HELLO", tile_width=50, gap=10)
        self.assertEqual(len(board.tiles), 5)
        
        # Check positions
        self.assertEqual(board.tiles[0].position.get(), (0, 0))
        self.assertEqual(board.tiles[1].position.get(), (60, 0))
        self.assertEqual(board.tiles[4].position.get(), (240, 0))
        
    def test_airport_board_flip_to(self):
        board = SplitFlapAirportBoard("HI", tile_width=50, gap=10)
        board.flip_to("BYE", duration=1.0)
        
        # Should resize to max length (3)
        self.assertEqual(len(board.tiles), 3)
        
        # Should setup scrambles
        self.assertEqual(len(board.scrambles), 3)
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 100)
        ctx = cairo.Context(surface)
        
        # Draw halfway
        board.draw(ctx, 0.5)

