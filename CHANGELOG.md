# Changelog

All notable changes to `cosmotech-run-orchestrator` are documented here.

## [2.1.0] - 2025

### Added
- **Visual Orchestrator GUI** (`csm-orc gui`): a new interactive browser-based interface for visualising and editing orchestration DAGs.
- **`CSM_RUN_TYPE` support**: the entrypoint now reads the `CSM_RUN_TYPE` environment variable (injected by the Cosmo Tech API) to decide which JSON template file to execute — defaults to `run.json`, but can be set to `delete` to execute `delete.json` instead. If the file for a non-`run` type is absent, the run is silently skipped rather than erroring.
- Improved i18n: translation keys are now split into smaller per-topic YAML files for easier maintenance.

### Fixed
- Logging message formatting when i18n is active.

---

## [2.0.2] - 2024

### Added
- `get_logger` now also accepts a **string** value for the `level` parameter (e.g. `"debug"`, `"INFO"`).

### Fixed
- Ensured that the logger created for step-parsing output has exactly one handler, preventing duplicate log lines.
- Internal loggers now use passthrough messages for steps and the entrypoint.

---

## [2.0.1] - 2024

### Fixed
- Corrected the published version tag (was mistakenly labelled 2.0.2 before release).

---

## [2.0.0] - 2024

### Added
- **Translation system** (`cosmotech.orchestrator.utils.translate`): all user-facing messages are now internationalised via YAML files under `cosmotech/translation/csm-orc/`. Supported languages at launch: `en-US`, `fr-FR`, `de-DE`, `es-ES`, `zh-CN`, `br`, `sjn`, `tlh`. Third-party packages can contribute their own translations by shipping a `cosmotech/translation/<name>/` namespace package.
- **Step-to-step data transfer**: steps can now declare `outputs` and `inputs` blocks in the JSON file to pass values between them. Output data is emitted via `log_data("name", "value")` (Python) or the shell token `CSM-OUTPUT-DATA:name:value`.
- **`CSM_LOCALE` environment variable** to select the active language at runtime.
- Tutorial pages for [Translations](docs/tutorial/translations.md) and [Step Data Transfer](docs/tutorial/step_data_transfer.md).

### Changed
- **Project structure reorganisation**: CLI entry-points moved from `cosmotech.orchestrator.console_scripts` to dedicated `cosmotech.csm_orc` and `cosmotech.csm_orc_api` modules.
- Updated examples and tutorials for the new project layout.

### Removed
- `table-reader` MkDocs plugin dependency.
- `generate_templates.py` documentation generation script (Command Templates section removed from nav).

---

## [1.6.3] - 2024

### Fixed
- Log messages that contain newline characters are now split correctly into individual log lines.

---

## [1.6.2] - 2024

### Changed
- Unified the format of all log lines for consistency.

---

## [1.6.1] - 2024

### Changed
- Colour output in the terminal is now fully parameterised; the `CSM_USE_RICH` environment variable controls whether Rich-formatted logging is used.

---

## [1.6.0] - 2024

### Added
- **`get_logger` helper** (`cosmotech.orchestrator.utils.logger.get_logger`): the logger factory previously shipped in *CosmoTech-Acceleration-Library* (CoAL) is now built into `run-orchestrator`. Plugin and template authors should import it from here going forward.

### Changed
- Cleaned up internal logger setup.

---

## [1.5.2] - 2024

### Deprecated
- `csm-orc run-step` is deprecated. Use `csm-orc run` with a single-step JSON file instead.

---

## [1.5.1] - 2024

### Fixed
- Duplicate exit handlers registered by multiple plugins are now deduplicated before execution.

---

## [1.5.0] - 2024

### Added
- **Exit handlers** via the `templates/on_exit/` folder inside a Library Plugin: any template placed there is automatically registered as an exit handler and runs after the orchestration completes, regardless of success or failure.
- `CSM_ORC_IS_SUCCESS` environment variable is injected into every exit handler (boolean string `"True"` / `"False"`).
- **`--exit-handlers / --no-exit-handlers`** flag for `csm-orc run` (env var `CSM_ORCHESTRATOR_USE_EXIT_HANDLERS`, default `true`): allows suppressing exit handlers for a specific run.
- Tutorial page for [Exit Handlers](docs/tutorial/exit_handlers.md).

---

## [1.4.3] - 2024

### Added
- Plugin template discovery now also searches **sub-folders** of the `templates/` directory, enabling richer plugin package layouts.

---

## [1.4.2] - 2024

### Fixed
- Removed a stray `logging.basicConfig` call that was causing duplicate or incorrectly formatted log output.

---

## [1.4.1] - 2024

### Changed
- The entrypoint now supports both `csm-simulator` (SDK ≥ 11.1.0) and the legacy `main` executable name, preferring `csm-simulator` when available.

---

## [1.4.0] - 2024

### Added
- **Direct Loki logging** from the entrypoint: when Loki environment variables are set, logs are forwarded to a Loki instance in addition to stdout.
- Pod-name enrichment in log scope headers, following Argo / API requirements.

### Changed
- Default log level changed from `WARNING` to `INFO`.
- Time format in log lines is now always 24-hour (`HH:MM:SS`).
- The entrypoint captures stdout and stderr from subprocesses and re-emits them through the structured logger.
- Improved detection of the log level when a subprocess emits lines without a visible level marker.

---

## [1.3.1] - 2024

### Added
- The entrypoint reads the `[EntrypointEnv]` section of `/pkg/share/project.csm` and injects those key-value pairs into the environment before starting the run, allowing container-level defaults to be defined at build time.

---

## [1.3.0] - 2024

### Changed
- **Removed all hard dependencies on CoAL (`CosmoTech-Acceleration-Library`) and `cosmotech-api`**. The orchestrator is now a standalone package; cloud-specific features (data download, API interaction) must be provided by other packages installed alongside it.
- Updated tutorials and examples to reflect the new standalone usage.

### Removed
- Legacy commands that depended on `cosmotech-api`: `csm-orc fetch-cloud-steps`, `csm-orc gen-from-legacy`, `csm-orc run-step` (legacy), `csm-orc scenario-data-download`, `csm-orc simulation-to-adx`, `csm-orc parameters-generator`, `csm-orc download-run-data`.
- Brewery legacy tutorial (moved to a separate example repository).

---

## [1.2.4] - 2024

### Changed
- Updated `cosmotech-api` dependency to `>=3.2`.
- Commands that previously used `sys.exit` or bare `return` for non-standard results now raise proper exceptions, making them composable.

---

## [1.2.3] - 2024

### Fixed
- Pinned CoAL and `cosmotech-api` dependency versions with compatible-release specifiers (`~=`) to avoid unintended upgrades.

---

## [1.2.2] - 2024

### Changed
- Updated dependency versions for compatibility.
