# Changelog

## [1.4.0] - 2026-08-25

### Added
- Isotope source activity (Ci / GBq) dynamic input and conversion:
  - Added unit selector (Curie / Gigabecquerel) on desktop and mobile with automatic $1\text{ Ci} = 37\text{ GBq}$ conversion.
  - Added Activity (Ci) input and slider to Mobile Step 3 (Exposure).
  - Exposure time calculations correctly scale inversely proportional to isotope activity ($t \propto 1/A$) in both Physics and R-Factor models.
- Dynamic UI simplification based on technique and source:
  - **X-Ray vs Isotope:** X-Ray shows Tube Voltage (kV) and Amperage (mA) while hiding isotope activity; Isotope shows Source Activity while hiding kV/mA and dynamically adjusting focal size and base factor labels.
  - **Analog vs Digital:** Analog Film hides digital detector, DDA panel, SRb resolution, duplex IQI and SNR inputs; Digital hides film class, film overlap and density inputs.
- Unit tests for dynamic UI visibility, isotope activity inverse proportionality and activity unit conversion.

### Fixed
- Fixed mobile `app_state.py` where `output_val` was hardcoded to `ma` (5.0), causing incorrect isotope exposure times.
- Fixed `calculate_exposure_time` parameter mapping in `app_state.py`.

## [1.3.5] - 2026-08-13

### Fixed
- Update check on Windows no longer fails with `SSL Certificate Verify Failed: missing authority key identifier`:
  - The updater now uses an explicit CA bundle from `certifi` instead of relying on the default OpenSSL store, which PyInstaller-frozen builds cannot always resolve
  - `certifi` added to `requirements.txt` and to the PyInstaller spec (`hiddenimports`) so the `cacert.pem` bundle is shipped inside the .exe/.dmg

## [1.3.4] - 2026-08-13

### Fixed
- "Standart ISO Şekli" combo box no longer blank: the input-panel and standard-tab combos are now kept in sync (`_sync_std_figure_tab`)
- Dynamic setup schematic now honours the selected theme: `draw_setup` was hard-coded to dark colours, so the light theme never applied
- Fixed crash (`KeyError: f_min_applied`) on the panel coverage path when a fixed-geometry case returned early

### Added
- User-provided source-to-object distance (f) and object-to-detector distance (b) inputs (digital mode, blank = auto):
  - `calculate_panel_exposures` accepts `f_source`/`b_object` overrides
  - Measured geometry is checked against applied SFD, wall thickness and the Clause 7.6 `f_min = C·d·b^(2/3)` geometric limit
- Base Exposure Multiplier input (default 1.0): scales the calculated exposure time and the compliance reference to compensate for field conditions (film batch, chemistry, detector ageing, material composition)
- TR/EN translations and tooltips for the new fields; PDF report row for the base multiplier

## [1.3.3] - 2026-08-11

### Added
- Flat-panel DDA coverage-based minimum exposure count per ISO 17636-2:2022 (Clauses 7.6/7.8)
- New panel inputs (digital only): active width/height, digital image overlap %, applied exposures
- Panel vs standard/graph vs applied exposure comparison in outputs and procedure compliance check
- PDF report rows for panel/applied/check exposure values

### Infrastructure
- Fully automated GitHub release pipeline: on push to `main`, a version bump in `src/core/version.py` triggers Windows .exe + macOS .dmg + Android APK build and GitHub Release creation
- Version is now read from `src/core/version.py` in the macOS bundle plist

## [1.3.2] - 2026-06-19

### Changed
- Extracted ASME B36.10 pipe data from inline dict in `input_panel.py` to shared `src/core/asme_b36.py`
- Created `ASME_B36_19_PIPES` dict for stainless steel pipe schedules (5S/10S/40S/80S)
- Generated `docs/asme_b36_10_19_pipe_data.json` — full pipe data export for external use
- Corrected outer diameter values per ASME B36.10-2022: 10"(273.1), 18"(457.2), 22"(558.8), 24"(609.6), 26"(660.4), 28"(711.2), 32"(812.8), 34"(863.6), 36"(914.4)
- Added missing schedules: SCH 160 + XXS for NPS 1/8–3/8
- Mobile Step 2 (Dimensions): replaced static 15-pipe list with full ASME B36.10 database + schedule sub-menu
- `buildozer.spec` source.include_patterns updated to include `src/core/asme_b36.py`

### Added
- Helper functions: `get_pipe_od()`, `get_pipe_schedules()`, `find_nps_by_od()`, `get_default_schedule()`
- 17 validation tests for `core.asme_b36`
- `pipe_schedule` attribute to `AppState` for mobile

## [1.3.1] - 2026-06-18

### Added (Mobile - KivyMD Android)
- Complete Material Design 3 responsive UI in KivyMD
- Compact wizard (<600dp): 5-step form (Technique → Dimensions → Exposure → Results → Sketch)
- Medium layout (600-839dp): NavigationRail (collapsed) + ScreenManager
- Expanded layout (≥840dp): NavigationRail (labeled) + ScreenManager
- Automatic foldable/layout switching via Window.size binding with state preservation
- Weld sketch engine: 10 Kivy Canvas drawing types (cross-section, longitudinal, double-wall, elliptical, superimposed, panoramic, girth weld, T-joint, source-film, defect map)
- PDF report generation with ReportLab + NotoSans font (Regular/Bold/Italic)
- Android Share Sheet integration (Pyjnius Intent ACTION_SEND)
- Singleton AppState manager with core calculator integration (~2200 lines)

### Infrastructure
- Buildozer spec for Android APK/AAB packaging
- GitHub Actions CI: Android APK build via kivy/buildozer-action
- Unified release pipeline: Windows .exe + macOS .dmg + Android APK under same version tag
- NotoSans static TTF fonts bundled for PDF generation

## [1.3.0] - 2026-06-13

### Added
- API 1104 defect types: slag, undercut, burn-through, cross-accumulation check
- Gradient-based density correction (ISO 17636-1 Annex C film gradient table)
- DWSI technique lookup from ISO 17636-1 Annex C
- Beam hardening approximation for X-ray
- QSettings persistence (window geometry, splitter sizes, theme, language, form state)
- Modular panel mixins (InputPanel, DefectPanel, WarningsCompliancePanel)

### Changed
- UI redesigned: 3-column horizontal splitter layout (inputs 25% | outputs+compliance 25% | sketch+warnings+defects 50%)
- Output values arranged vertically (QVBoxLayout) instead of grid
- Sketch displayed square in right panel top 50%
- Procedure compliance panel moved below calculation results
- Splitter handles thickened to 8px with hover color effects
- QGroupBox card-style background for visual depth
- Input field border-radius increased to 6px for softer look

### Fixed
- Restored missing `txt_app_time`, `lbl_app_time`, `cmb_app_wire`, `lbl_app_wire` widgets
- Fixed `cmb_app_duplex` userData assignment (currentData returned None)
- Replaced stray `print()` call with `logger.error()` in report module

## [1.2.0] - 2026-06-08

### Added
- ISO 17636-2 digital detector support (CR/DDA with DQE-based speed modeling)
- API 1104 defect evaluation module (crack, IP, IF, IC, porosity)
- Level 3 Authority exceptions panel (voltage override, distance compensation, etc.)
- Procedure compliance checker (applied vs required parameters)
- Multi-language support (Turkish / English) with full UI retranslation
- Dynamic weld geometry sketch with matplotlib (Qt Agg canvas)
- Standard ISO 17636 figure schematics (Figures 5, 6, 7, 11, 12, 13)
- Exposure chart database (R-Factor SCRATA + Type X chart)
- Filter/screen recommendations per ISO 17636-1 Table 1
- Automatic update checker via GitHub Releases
- ASME B36.10 standard pipe dimensions table
- PDF inspection report generation with ReportLab
- Dark/Light theme toggle (Catppuccin Mocha / Professional Slate)
- Edge case handling for extreme thicknesses, zero values, and missing data
- Comprehensive test suite (133 tests)

### Changed
- Version management centralized to `src/core/version.py`
- CI/CD pipeline now builds universal2 macOS binaries
- GitHub Release workflow extracts notes from CHANGELOG.md
- DMG volume name is dynamically set from git tag
- Windows .exe renamed with version and platform suffix

### Fixed
- GitHub repo URL typo in updater (`Radiogrphy` -> `Radiography`)
- English translation strings cleaned of Turkish words
- Theme contrast in popup dialogs (QMessageBox, Level3 dialog)
- Info button and output label colors adapt to active theme
- Sketch canvas colors update on theme toggle

## [1.1.0] - 2026-05-15

### Added
- Initial dual-language support framework
- Basic PDF report generation
- Weld geometry calculator (SWSI, DWSI, DWDI)
- ISO 17636-1 Class A/B compliance checks
- Geometric unsharpness and minimum distance calculations

## [1.0.0] - 2026-04-01

### Added
- First stable release
- Core RT exposure time calculator
- PyInstaller packaging for Windows and macOS
- Basic Qt6 GUI with input/output form
