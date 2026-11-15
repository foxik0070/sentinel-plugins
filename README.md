# Sentinel Plugins

![sentinel-plugins](sentinel_plugins.png)
![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Detectors](https://img.shields.io/badge/detectors-10-blue)

**Volitelné detektory pro [Sentinel Commander](https://github.com/foxik0070/Sentinel).**

Sentinel si v sobě nechává jen základ — `base.py` (rozhraní `BaseDetector`)
a dva detektory, bez kterých nedává smysl: `system_detector` a
`services_detector`. Všechno ostatní žije tady a nasazuje se **balíčkem**
`sentinel-plugins` (`.deb` / `.rpm`), nezávisle na vydání Sentinelu.

---

## Detektory

| Plugin | Vstup | Závažnost | AI | Samoopravné |
|---|---|---|---|---|
| `audit_detector` | `audit.log` | WARN / CRIT | — | — |
| `availability_detector` | `availability.log` | CRITICAL | — | ✓ STATUS:UP |
| `capacity_detector` | `capacity.log` | WARN / CRIT | — | — |
| `ha_detector` | Home Assistant JSON | TELEMETRY / CRIT | — | — |
| `port_detector` | `ports.log` (`ss -tuln`) | WARN / CRIT | — | — |
| `security_detector` | `security.log` (fail2ban) | WARNING | — | — |
| `storage_detector` | `storage.log` (ZFS) | CRITICAL | — | ✓ STATUS:HEALTHY |
| `temperature_detector` | `temperature.log` | WARN / CRIT | — | ✓ < WARN_LIMIT |
| `detector_universal_security` | `auth.log` / `syslog` | INFO–CRIT | ✓ AI fronta | — |
| `detector_windows` | Windows event log | WARN / CRIT | — | — |

V Sentinelu zůstávají `system_detector` (jádro) a `services_detector` (systemd).

---

## Instalace

### Balíčkem (doporučeno)

```bash
# Debian / Ubuntu
apt install sentinel-plugins
# RHEL a odvozené
dnf install sentinel-plugins
```

Detektory se nainstalují do `/opt/sentinel-plugins`. Sentinel je tam najde,
protože `plugin_dir` smí být **seznam adresářů**:

```yaml
plugin_dir:
  - /opt/Sentinel/sentinel/plugins   # základ, který veze Sentinel
  - /opt/sentinel-plugins            # tenhle balíček
detectors:
  - plugin: port_detector
    match_pattern: ports.log
  - plugin: security_detector
    match_pattern: security.log
```

Hledá se v uvedeném pořadí, takže při shodě jmen vyhraje adresář uvedený dřív.
Jediný řetězec místo seznamu funguje jako dřív.

### Ručně

```bash
git clone https://github.com/foxik0070/sentinel-plugins /opt/sentinel-plugins
```

Detektory se načítají při startu a při hot-reloadu, restart není potřeba.

---

## Vlastní detektor

Detektor je soubor `<jméno>.py` s třídou `Detector`, která dědí
`api.BaseDetector`. Plugin manager ho načte podle jména z `config.yaml`
a volá `process()` s dávkou nových řádků:

```python
from datetime import datetime, timezone
from sentinel import api


class Detector(api.BaseDetector):
    def __init__(self, name, config_params=None):
        super().__init__(name, config_params)

    def process(self, lines, file_path):
        if not file_path.endswith("muj.log"):
            return
        host = "server1"
        for line in lines:
            key = f"MUJ_PROBLEM|{host}"
            if "ERROR" in line:
                api.report_problem(key, {
                    "status": "active",
                    "last_line": line.strip(),
                    "channel_type": "infra",
                    "host": host,
                    "cluster": api.get_infrastructure_label(file_path),
                    "log_file": file_path,
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "missing_count": 0,
                })
            else:
                api.mark_resolved(key)
```

`report_problem(key, data)` bere **slovník**, ne pojmenované argumenty. Klíč je
identita problému — stejný klíč podruhé znamená tentýž problém, ne nový.
`mark_resolved(key)` je druhá polovina kontraktu: bez ní issue visí i po tom,
co problém pominul. Nejkratší hotový příklad je `audit_detector.py`.

Pokud detektor v `config.yaml` je, ale jeho soubor se nenajde, Sentinel na to
**upozorní** vlastním issue (`SENTINEL|detectors_missing`, critical). Tiché
nenačtení už jednou stálo dva dny falešného „všechno OK".

---

## Architektura

```
log soubor (tail)
    │
    ▼
plugin_manager.py  — hledá <jméno>.py v adresářích z plugin_dir
    │
    ▼
Detector.process(lines, file_path)
    │
    ▼
state.save_problem() → SQLite → Socket.IO → notifier.py
```

---

## Související

- [Sentinel Commander](https://github.com/foxik0070/Sentinel) — načítá a spouští tyhle detektory
- `sentinel-plugins-it4i` — detektory pro HPC prostředí, vlastní repozitář

Dokumentace: **https://sentinel-docs.foxik-iot.cz/**

---

## Licence

MIT — viz [LICENSE](LICENSE). Copyright © 2026 foxik0070.
