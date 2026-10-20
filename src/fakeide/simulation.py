"""Deterministic, offline-only developer-workflow theatre. No commands are executed."""
from __future__ import annotations
from dataclasses import dataclass
import random

FILES = (
    'src/core/runtime_engine.cpp',
    'src/core/task_scheduler.cpp',
    'src/render/renderer.cpp',
    'src/runtime/memory_pool.cpp',
    'src/diagnostics/analyzer.cpp',
    'include/runtime/config.hpp',
)

HEADERS = {
    'src/core/runtime_engine.cpp': '''#include "runtime_engine.hpp"
#include <algorithm>
#include <chrono>
#include <memory>

namespace runtime {

class RuntimeEngine final {
public:
    explicit RuntimeEngine(Config config) : config_(config) {}
    void update(float deltaTime);
    bool initialize() noexcept;
private:
    Config config_;
    std::vector<Task> pending_;
    uint64_t frameIndex_ = 0;
};
''',
    'src/core/task_scheduler.cpp': '''#include "task_scheduler.hpp"
#include <atomic>
#include <optional>

namespace runtime {

constexpr size_t kMaxWorkers = 16;
struct TaskContext {
    std::atomic<uint64_t> completed{0};
    std::optional<Task> active;
};
''',
    'src/render/renderer.cpp': '''#include "renderer.hpp"
#include <array>
#include <cstdint>

namespace render {

struct RenderState final {
    uint32_t width = 1920;
    uint32_t height = 1080;
    bool initialized = false;
};
''',
    'src/runtime/memory_pool.cpp': '''#include "memory_pool.hpp"
#include <cstddef>
#include <new>

namespace runtime {

constexpr size_t kBlockAlignment = 64;
struct AllocationStats {
    size_t allocated = 0;
    size_t highWatermark = 0;
};
''',
    'src/diagnostics/analyzer.cpp': '''#include "analyzer.hpp"
#include <string_view>
#include <vector>

namespace diagnostics {

struct Diagnostic {
    Severity severity = Severity::Info;
    std::string_view message;
};
''',
    'include/runtime/config.hpp': '''#pragma once
#include <cstdint>

namespace runtime {

struct Config final {
    uint32_t workerCount = 8;
    uint32_t queueCapacity = 4096;
    bool enableDiagnostics = true;
};
''',
}

CODE_LINES = (
    '    // Update subsystems in a stable, deterministic order.',
    '    const auto elapsed = std::chrono::steady_clock::now();',
    '    if (!config_.enableDiagnostics) return;',
    '    auto nextIndex = static_cast<uint32_t>(frameIndex_ % 128);',
    '    const bool ready = pending_.size() < config_.queueCapacity;',
    '    if (ready && nextIndex != 0) {',
    '        scheduler_.flushPending(nextIndex);',
    '        telemetry_.recordFrame(frameIndex_);',
    '    }',
    '    constexpr float epsilon = 0.0001f;',
    '    const float clamped = std::clamp(deltaTime, 0.0f, 0.1f);',
    '    if (clamped > epsilon) updateWorkers(clamped);',
    '    ++frameIndex_;',
    '',
)

WARNINGS = (
    ('C4244', 'conversion from size_t to uint32_t, possible loss of data'),
    ('C4100', 'unreferenced formal parameter: context'),
    ('C26812', 'prefer enum class over enum'),
    ('C26495', 'member variable not initialized'),
    ('C6262', 'function uses significant stack space'),
)

@dataclass(frozen=True)
class Event:
    kind: str  # log | info | warn | error | code | build | tests | file
    message: str
    file: str = ''
    line: int = 0


class SimEngine:
    def __init__(self, seed: int = 125) -> None:
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        self.tick_count = 0
        self.active_file = FILES[0]
        self.file_index = 0
        self.line_index = 0
        self.warning_count = 0
        self.error_count = 0
        self.build_count = 0
        self.test_count = 0
        self.phase = 'EDITING'
        self._queue: list[Event] = []
        self.last_build_ok: bool | None = None

    def cpu(self) -> int:
        return min(94, 7 + self._rng.randrange(12, 44) + (24 if self.phase == 'BUILDING' else 0))

    def ram(self) -> str:
        return f'{5.1 + (self.tick_count % 117) / 45:.1f} GB'

    def inject_warning(self) -> Event:
        code, description = self._rng.choice(WARNINGS)
        self.warning_count += 1
        return Event('warn', f'warning {code}: {description}', self.active_file, self._rng.randrange(22, 240))

    def inject_error(self) -> Event:
        self.error_count += 1
        return Event('error', "error C2065: 'workerContext': undeclared identifier", self.active_file, 176)

    def start_build(self, fail: bool = False) -> Event:
        self.build_count += 1
        self.phase = 'BUILDING'
        self.last_build_ok = None
        idx = self.build_count
        queue: list[Event] = [
            Event('build', f'Build started: Solution: 125A Runtime, Configuration: Release x64 (#{idx})'),
            Event('log', 'MSBuild version 17.12.12+1cce77968 for .NET Framework'),
            Event('log', 'Preparing incremental compilation...'),
        ]
        for file in FILES[:5]:
            queue.append(Event('log', f'  Compiling {file.split("/")[-1]}', file))
        if self._rng.random() < 0.8:
            queue.append(self.inject_warning())
        if fail:
            queue.append(self.inject_error())
            queue.append(Event('error', 'LINK : fatal error LNK1181: cannot open input file runtime_core.lib'))
            queue.append(Event('build', 'Build FAILED. 0 succeeded, 1 failed, 1 warning.'))
        else:
            queue.extend([
                Event('log', '  Generating code...'),
                Event('log', '  125A Runtime.vcxproj -> bin\\x64\\Release\\Runtime.exe'),
                Event('build', 'Build succeeded. 1 succeeded, 0 failed, 1 warning.'),
                Event('tests', 'Discovering test cases: 18 found'),
                Event('tests', 'Running scheduler / memory / rendering regression suite...'),
                Event('tests', '18/18 tests passed (simulated)'),
            ])
        self._queue = queue
        return Event('info', 'Simulation: build sequence queued')

    def step(self) -> list[Event]:
        self.tick_count += 1
        if self._queue:
            event = self._queue.pop(0)
            if not self._queue:
                self.phase = 'EDITING'
                self.last_build_ok = not any(token in event.message.lower() for token in ('failed', 'error'))
                if event.kind == 'tests':
                    self.test_count += 1
            return [event]
        events: list[Event] = []
        if self.tick_count % 48 == 0:
            self.file_index = (self.file_index + 1) % len(FILES)
            self.active_file = FILES[self.file_index]
            events.append(Event('file', self.active_file, self.active_file))
        if self.tick_count % 5 == 0:
            line = CODE_LINES[self.line_index % len(CODE_LINES)]
            self.line_index += 1
            events.append(Event('code', line, self.active_file))
        if self.tick_count % 32 == 0:
            events.append(Event('info', self._rng.choice([
                'IntelliSense: database up to date',
                'Static analysis: checking updated translation units',
                'Incremental parser: 6 files indexed',
                'Git: working tree clean (simulated)',
            ])))
        if self.tick_count % 97 == 0:
            events.append(self.inject_warning())
        if self.tick_count % 220 == 0:
            self.start_build()
        return events
