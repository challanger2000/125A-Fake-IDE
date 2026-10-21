"""Deterministic theatre director for the Vibe Coding Edition.

This module never executes processes or external commands.  Crashes are
scene events, not unhandled exceptions or operating-system failures.
"""
from __future__ import annotations

from dataclasses import dataclass
import random

from .simulation import Event

CLAUDE_LINES = (
    'Kein Problem! Ich habe den Fehler bereits behoben.',
    'Alle Änderungen sind konsistent. Build sollte jetzt PASS sein.',
    'Ich habe die Ursache gefunden. Es war nur eine Kleinigkeit.',
    'Fix implementiert. Bitte erneut in Studio One testen.',
    'Die Architektur ist jetzt vollständig stabil.',
    'Natürlich! Der Multi-Out-Pfad ist jetzt korrekt verdrahtet.',
    'Der Code ist sauber. Ich sehe keine weiteren Risiken.',
    'Ich habe den vorherigen Fix noch einmal gefixt.',
    'PASS. Die verbleibenden 27 Warnungen sind unkritisch.',
    'Das ist erwartetes Verhalten. Ich passe die Tests an.',
    'Ich habe einen vollständigen Deep Audit durchgeführt.',
    'Der Rollback war erfolgreich. Keine Daten verloren.',
    'Jetzt aber wirklich. Alle Regressionen erfolgreich.',
    'Es gibt keinen Grund zur Sorge. Ich bin zuversichtlich.',
)

REALITY_LINES = (
    'runtime_engine.cpp(176): error C2065: workerContext nicht deklariert',
    'processor.cpp(322): error C2039: getBusInfo ist kein Member',
    'Studio One: Multi-Out zeigt weiterhin nur Main',
    'RECALL FAILED: Pattern nach Projektneustart nicht wiederhergestellt',
    'MIDI NOTE-OFF: 14 hängende Noten gefunden',
    'GUI: Zoom 150% -> hit-test offset 86 px',
    'WARNING: Start ab Takt 2 springt auf Step 17',
    'LINK : fatal error LNK1104: cannot open file runtime_core.lib',
    'CI: 47 Tests passed, 1 essential manual test not performed',
    'PROCESS: unexpected exception in Editor::attached()',
    'Roll back complete: 3 new failures detected',
    'Sampler: sample buffer changed during project recall',
)

BACKLOG = (
    'Multi-Out nur Main',
    'MIDI-Noten hängen',
    'Pattern-Recall defekt',
    'Zoom 150% verschoben',
    'Start ab Takt 2 falsch',
    'Build schon wieder rot',
    'GUI überlappt',
    'Release V1 verschoben',
    'Nächster Fehler?',
)

CRASH_TITLES = (
    'Access violation in runtime_engine.dll',
    'Unhandled exception: 0xC0000005',
    'Editor thread stopped responding',
    'Fatal application error: null pointer read',
)


@dataclass
class CrashState:
    """Pure, verifiable state for a fake crash with idempotent recovery."""
    active: bool = False
    crashes: int = 0
    recoveries: int = 0

    def trigger(self) -> bool:
        if self.active:
            return False
        self.active = True
        self.crashes += 1
        return True

    def recover(self) -> bool:
        if not self.active:
            return False
        self.active = False
        self.recoveries += 1
        return True

    def reset(self) -> None:
        self.active = False
        self.crashes = 0
        self.recoveries = 0


class VibeDirector:
    """Deterministic scripted contradiction: confident AI, broken compiler."""

    def __init__(self, seed: int = 2026) -> None:
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        self.message_index = 0
        self.problem_index = 0
        self.task_index = 0

    def initial_message(self) -> str:
        return 'Ich habe den Code analysiert. Sieht gut aus! Bereit zum Bauen.'

    def next_claim(self) -> Event:
        msg = CLAUDE_LINES[self.message_index % len(CLAUDE_LINES)]
        self.message_index += 1
        return Event('claude', msg)

    def next_problem(self) -> Event:
        msg = REALITY_LINES[self.problem_index % len(REALITY_LINES)]
        self.problem_index += 1
        return Event('reality', msg)

    def next_task(self) -> Event:
        msg = BACKLOG[self.task_index % len(BACKLOG)]
        self.task_index += 1
        return Event('task', msg)

    def step(self, ticks: int, mode: str) -> list[Event]:
        """Issue bounded events at repeatable virtual times.

        'Normal' keeps most of the original IDE calm, 'Vibe' introduces
        regular contradictions, and 'Panik' adds frequent staged crashes.
        """
        if ticks < 1 or mode not in ('Normal', 'Vibe', 'Panik'):
            return []
        ai_period = {'Normal': 155, 'Vibe': 75, 'Panik': 38}[mode]
        reality_period = {'Normal': 270, 'Vibe': 117, 'Panik': 67}[mode]
        task_period = {'Normal': 490, 'Vibe': 245, 'Panik': 110}[mode]
        crash_period = {'Normal': 0, 'Vibe': 560, 'Panik': 300}[mode]
        events: list[Event] = []
        if ticks % ai_period == 0:
            events.append(self.next_claim())
        if ticks % reality_period == 0:
            events.append(self.next_problem())
        if ticks % task_period == 0:
            events.append(self.next_task())
        if crash_period and ticks % crash_period == 0:
            events.append(Event('crash', CRASH_TITLES[self._rng.randrange(len(CRASH_TITLES))]))
        return events
