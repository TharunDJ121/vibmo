# E2E Test Infra: Motio / Vibmo 100+ Asset Expansion & Modernization

## Test Philosophy
- Opaque-box, requirement-driven, and multi-tier verification.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Feature Combinations + Real-World Workload Testing.
- 100% pytest pass rate across all modules + zero-defect visual validation (`scene.validate()`, `scene.storyboard()`, `scene.render()`).

---

## Test Architecture
- **Test Runner**: `pytest`
- **Asset Suites**:
  - `tests/audio/` (Procedural sound synthesis)
  - `tests/fx/` (Animated backdrops & Post-FX shaders)
  - `tests/product/` (Hardware chassis & AI UI suites)
  - `tests/charts/` (Financial, 3D, and statistical charts)
  - `tests/typography/` (Kinetic typography suites)
  - `tests/templates/` (Turnkey templates)
  - `tests/components/` & `tests/layout/` (Core primitives & layout)
- **E2E Visual Showcase**:
  - Script: `examples/asset_expansion_full_showcase.py`
  - Validation: `scene.validate()` with zero bounds overflows, zero keyframe time overflows, zero frame crashes.
  - Storyboard: Programmatic contact sheet generation (`scene.storyboard()`).

---

## Coverage Thresholds & Tiers
- **Tier 1: Feature Coverage**: Verify instantiation, default parameters, and basic rendering for all 100+ features.
- **Tier 2: Boundary & Corner Cases**: Empty inputs, extreme dimensions, zero durations, max values, headless/CPU fallbacks.
- **Tier 3: Cross-Feature Combinations**: Composing hardware chassis with AI UI, combining charts with backdrops, layering shaders on kinetic typography.
- **Tier 4: Real-World Application Scenarios**: Turnkey templates, master full showcase execution, multi-scene compositions with synchronized procedural audio.
