import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from fakeide.simulation import FILES, HEADERS, Event, SimEngine


class SimulationTests(unittest.TestCase):
    def test_all_files_have_initial_display(self):
        self.assertEqual(set(FILES), set(HEADERS))
        self.assertTrue(all(HEADERS[file].strip() for file in FILES))

    def test_initial_state_and_reset(self):
        engine = SimEngine()
        self.assertEqual(engine.phase, 'EDITING')
        self.assertEqual(engine.active_file, FILES[0])
        engine.inject_warning()
        engine.reset()
        self.assertEqual(engine.warning_count, 0)
        self.assertEqual(engine.error_count, 0)
        self.assertEqual(engine.build_count, 0)

    def test_normal_build_is_staged_and_returns_to_editing(self):
        engine = SimEngine(seed=12)
        engine.start_build()
        self.assertEqual(engine.phase, 'BUILDING')
        events = []
        for _ in range(40):
            events.extend(engine.step())
            if engine.phase == 'EDITING':
                break
        self.assertEqual(engine.phase, 'EDITING')
        self.assertTrue(any('Build succeeded.' in e.message for e in events))
        self.assertEqual(engine.test_count, 1)
        self.assertIs(engine.last_build_ok, True)

    def test_failed_build_is_not_reported_as_success(self):
        engine = SimEngine(seed=3)
        engine.start_build(fail=True)
        events = []
        while engine.phase == 'BUILDING':
            events += engine.step()
        self.assertTrue(any(e.kind == 'error' for e in events))
        self.assertTrue(any('Build FAILED.' in e.message for e in events))
        self.assertIs(engine.last_build_ok, False)
        self.assertEqual(engine.test_count, 0)

    def test_typing_and_file_switch(self):
        engine = SimEngine()
        events = [e for _ in range(50) for e in engine.step()]
        self.assertTrue(any(e.kind == 'code' for e in events))
        self.assertTrue(any(e.kind == 'file' for e in events))
        self.assertEqual(engine.active_file, FILES[1])

    def test_warning_is_diagnostic_not_command(self):
        e = SimEngine().inject_warning()
        self.assertEqual(e.kind, 'warn')
        self.assertIn('warning C', e.message)
        self.assertIn(e.file, FILES)
        self.assertGreater(e.line, 0)


if __name__ == '__main__':
    unittest.main()
