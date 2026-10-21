import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from fakeide.vibe import BACKLOG, CrashState, VibeDirector


class VibeTests(unittest.TestCase):
    def test_normal_mode_has_no_automatic_crashes(self):
        d = VibeDirector()
        self.assertFalse(any(e.kind == 'crash' for n in range(1, 1201)
                             for e in d.step(n, 'Normal')))

    def test_vibe_mode_emits_confidence_and_reality(self):
        d = VibeDirector()
        events = [e for n in range(1, 1201) for e in d.step(n, 'Vibe')]
        kinds = {event.kind for event in events}
        self.assertTrue({'claude', 'reality', 'task', 'crash'} <= kinds)
        self.assertTrue(all(event.message for event in events))

    def test_panic_mode_is_more_active(self):
        def count(mode):
            d = VibeDirector()
            return sum(len(d.step(t, mode)) for t in range(1, 1001))
        self.assertGreater(count('Panik'), count('Vibe'))
        self.assertGreater(count('Vibe'), count('Normal'))

    def test_crash_state_never_crashes_actual_process(self):
        state = CrashState()
        self.assertTrue(state.trigger())
        self.assertFalse(state.trigger())
        self.assertEqual(state.crashes, 1)
        self.assertTrue(state.recover())
        self.assertFalse(state.recover())
        self.assertEqual(state.recoveries, 1)
        self.assertFalse(state.active)

    def test_director_reset_replays_dialogue_from_start(self):
        d = VibeDirector()
        first = d.next_claim().message
        d.next_problem()
        d.next_task()
        d.reset()
        self.assertEqual(d.next_claim().message, first)
        self.assertEqual(d.next_task().message, BACKLOG[0])

    def test_invalid_mode_does_not_produce_events(self):
        d = VibeDirector()
        self.assertEqual(d.step(0, 'Panik'), [])
        self.assertEqual(d.step(33, 'unknown'), [])


if __name__ == '__main__':
    unittest.main()
