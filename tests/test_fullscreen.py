"""Headless regressions for the fullscreen controls and editor-focus key routing."""
from __future__ import annotations

import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from fakeide.app import FakeIDEApp


class FakeWindow:
    def __init__(self):
        self.is_fullscreen = False

    def attributes(self, name, value=None):
        if name != '-fullscreen':
            raise AssertionError('unexpected window attribute')
        if value is not None:
            self.is_fullscreen = bool(value)
        return self.is_fullscreen


class FullscreenTests(unittest.TestCase):
    def setUp(self):
        self.app = FakeIDEApp.__new__(FakeIDEApp)
        self.app.root = FakeWindow()
        self.app.fullscreen_button = Mock()
        self.app._toggle = Mock()
        self.app._warning = Mock()
        self.app._start_build = Mock()
        self.app._reset = Mock()

    @staticmethod
    def key(name, state=0):
        return SimpleNamespace(keysym=name, state=state)

    def test_fullscreen_button_and_escape(self):
        self.app._fullscreen()
        self.assertTrue(self.app.root.is_fullscreen)
        self.app.fullscreen_button.config.assert_called_with(text='▣ Fenster (F11)')
        self.assertEqual(self.app._handle_shortcut(self.key('Escape')), 'break')
        self.assertFalse(self.app.root.is_fullscreen)
        self.app.fullscreen_button.config.assert_called_with(text='⛶ Vollbild (F11)')

    def test_f11_works_when_editor_has_focus(self):
        self.assertEqual(self.app._on_code_key(self.key('F11')), 'break')
        self.assertTrue(self.app.root.is_fullscreen)
        self.assertEqual(self.app._on_code_key(self.key('F11')), 'break')
        self.assertFalse(self.app.root.is_fullscreen)

    def test_editor_blocks_typing_but_preserves_shortcuts(self):
        self.assertEqual(self.app._on_code_key(self.key('a')), 'break')
        self.assertEqual(self.app._on_code_key(self.key('F5')), 'break')
        self.app._toggle.assert_called_once_with()
        self.assertEqual(self.app._on_code_key(self.key('F6')), 'break')
        self.app._warning.assert_called_once_with()
        self.assertEqual(self.app._on_code_key(self.key('F7')), 'break')
        self.app._start_build.assert_called_once_with()
        self.assertEqual(self.app._on_code_key(self.key('r', 0x4)), 'break')
        self.app._reset.assert_called_once_with()

    def test_escape_does_not_enter_fullscreen(self):
        self.assertEqual(self.app._on_code_key(self.key('Escape')), 'break')
        self.assertFalse(self.app.root.is_fullscreen)
        self.app.fullscreen_button.config.assert_not_called()


if __name__ == '__main__':
    unittest.main()
