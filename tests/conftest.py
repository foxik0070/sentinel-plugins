"""Detektory potrebuji Sentinel — testy se bez nej nedaji spustit.

Sentinel se hleda v SENTINEL_SRC, pak jako sourozenec tohohle repozitare
(tak to ma monorepo Sentinel-complete) a nakonec v /opt/Sentinel. Kdyz
nikde neni, testy se preskoci misto padu pri sberu.

Detektory se navic importuji jako `sentinel.plugins.<jmeno>`, protoze tak
je registruje plugin manager a diky tomu jim funguji relativni importy.
Soubory ale lezi tady, ne v Sentinelu — proto se adresar pripoji do cesty
balicku `sentinel.plugins`.
"""
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_sentinel():
    for cand in (os.environ.get("SENTINEL_SRC"),
                 os.path.join(os.path.dirname(_HERE), "Sentinel"),
                 "/opt/Sentinel"):
        if cand and os.path.isdir(os.path.join(cand, "sentinel")):
            return cand
    return None


_ROOT = _find_sentinel()
if _ROOT is None:
    pytest.skip("Sentinel nenalezen (nastavte SENTINEL_SRC)", allow_module_level=True)

if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import sentinel.plugins  # noqa: E402

# Detektory z tohohle repozitare se tvari jako soucast sentinel.plugins.
if _HERE not in sentinel.plugins.__path__:
    sentinel.plugins.__path__.append(_HERE)
