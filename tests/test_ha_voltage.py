"""Podpeti se hlasi jen u senzoru, ktere meri sit.

Zachyt z provozu: `sensor.game_machine_..._nct6683_voltage_2` hlasilo
"Podpeti nebo vypadek v siti (0.0 V)". Je to napetova vetev zakladni desky
(0-12 V) na stroji, ktery byl vetsinu casu vypnuty — ne vypadek proudu.
"""
import json

import pytest

import ha_detector


@pytest.fixture
def det(tmp_path, monkeypatch):
    monkeypatch.setattr(ha_detector._cfg_mod, "LOG_DIR", str(tmp_path), raising=False)
    monkeypatch.setattr(ha_detector._cfg_mod, "HA_THRESHOLDS", {}, raising=False)
    return ha_detector.Detector("ha_detector")


def test_board_rail_never_alerts(det):
    """Vetev desky se k 230 V nikdy nepriblizi, takze se nebere jako sit."""
    for v in (3.3, 5.0, 12.0, 0.0):
        det._is_mains_voltage("sensor.nct6683_voltage_2", v)
    assert det._is_mains_voltage("sensor.nct6683_voltage_2", 0.0) is False


def test_mains_sensor_alerts_after_showing_mains_value(det):
    """Co uz jednou ukazalo sitove napeti, se hlidat ma."""
    det._is_mains_voltage("sensor.ups_input_voltage", 231.4)
    assert det._is_mains_voltage("sensor.ups_input_voltage", 0.0) is True


def test_whitelist_overrides_history(det, monkeypatch):
    monkeypatch.setattr(ha_detector._cfg_mod, "HA_THRESHOLDS",
                        {"voltage_entities": ["sensor.ups_*"]}, raising=False)
    assert det._is_mains_voltage("sensor.ups_input_voltage", 0.0) is True
    assert det._is_mains_voltage("sensor.nct6683_voltage_2", 0.0) is False


def test_seen_values_survive_restart(det, tmp_path, monkeypatch):
    det._is_mains_voltage("sensor.ups_input_voltage", 230.0)
    det._save_volt_seen()
    fresh = ha_detector.Detector("ha_detector")
    assert fresh._is_mains_voltage("sensor.ups_input_voltage", 0.0) is True


def test_ignore_entities_glob(monkeypatch):
    monkeypatch.setattr(ha_detector._cfg_mod, "HA_THRESHOLDS",
                        {"ignore_entities": ["sensor.game_machine_*"]}, raising=False)
    assert ha_detector._matches("sensor.game_machine_hardware_sensor_x",
                                ha_detector._globs("ignore_entities"))
    assert not ha_detector._matches("sensor.ups_input_voltage",
                                    ha_detector._globs("ignore_entities"))
