# Sentinel Plugins

![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![Detectors](https://img.shields.io/badge/detectors-11-blue)

**Detector plugins for Sentinel Commander.**

This repository contains the 11 detector plugins that run inside [Sentinel Commander](https://github.com/foxik0070/Sentinel). Each plugin watches a specific log file or data source, parses events, and feeds them into the Sentinel issue pipeline. Plugins are hot-reloaded — no restart required when adding or updating.

---

## Detectors

| Plugin | Input | Severity | AI | Auto-heal |
|---|---|---|---|---|
| `audit_detector` | `audit.log` | WARN / CRIT | — | — |
| `availability_detector` | `availability.log` | CRITICAL | — | ✓ STATUS:UP |
| `capacity_detector` | `capacity.log` | WARN / CRIT | — | — |
| `ha_detector` | Home Assistant JSON | TELEMETRY / CRIT | — | — |
| `port_detector` | `ports.log` (`ss -tuln`) | WARN / CRIT | — | — |
| `security_detector` | `security.log` (fail2ban) | WARNING | — | — |
| `services_detector` | `services.log` | CRITICAL | — | — |
| `storage_detector` | `storage.log` (ZFS) | CRITICAL | — | ✓ STATUS:HEALTHY |
| `system_detector` | `system.log` (kernel) | CRITICAL | — | — |
| `temperature_detector` | `temperature.log` | WARN / CRIT | — | ✓ < WARN_LIMIT |
| `detector_universal_security` | `auth.log` / `syslog` | INFO–CRIT | ✓ AI enqueue | — |

---

## Usage

### With Sentinel Commander

Plugins are loaded automatically from the directory configured in `config.yaml`:

```yaml
plugin_dir: /opt/Sentinel/sentinel/plugins
detectors:
  - audit_detector
  - capacity_detector
  - security_detector
  - detector_universal_security
  # add/remove as needed
```

Copy the plugins you need:

```bash
git clone https://github.com/foxik0070/sentinel-plugins /tmp/sentinel-plugins
cp /tmp/sentinel-plugins/*.py /opt/Sentinel/sentinel/plugins/
# Sentinel hot-reloads them automatically
```

### Writing a Custom Detector

All detectors extend `BaseDetector` from `base.py`:

```python
from base import BaseDetector

class MyDetector(BaseDetector):
    def detect(self, line: str) -> dict | None:
        if "ERROR" in line:
            return {
                "severity": "HIGH",
                "category": "INFRA",
                "message": f"Error detected: {line.strip()}",
            }
        return None
```

Register it in `config.yaml` under `detectors:` and Sentinel picks it up on the next reload.

---

## Architecture

```
Log file (inotify tail)
    │
    ▼
plugin_manager.py
    │  calls detect(line) for each enabled plugin
    ▼
*_detector.py → returns issue dict or None
    │
    ▼
state.save_problem() → SQLite → Socket.IO → notifier.py
```

---

## Documentation

Full documentation: **https://sentinel-docs.example.com**

---

## Related

- [Sentinel Commander](https://github.com/foxik0070/Sentinel) — loads and runs these plugins

---

## License

MIT — see [LICENSE](LICENSE). Copyright © 2026 foxik0070.
