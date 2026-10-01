import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from dali.address import DeviceShort, InstanceNumber
from dali.command import NumericResponse
from dali.device.general import QueryInstanceType
from dali.device.helpers import check_bad_rsp
from dali.driver.serial import DriverLubaRs232


@pytest.mark.asyncio
async def test_timed_out_query_reports_missing_value():
    """A query that times out must return the command's own response type.

    A bare Response(None) passes check_bad_rsp while its value is None, which
    leaked into control-device autodiscovery and crashed on int(None).
    """
    driver = DriverLubaRs232("luba232:/dev/ttyACM0")
    driver._connected.set()
    protocol = MagicMock()
    protocol.reset_dali_response = MagicMock()
    protocol.send_dali_command = AsyncMock()
    protocol.wait_dali_raw_response = AsyncMock(side_effect=asyncio.TimeoutError)
    driver._protocol = protocol

    response = await driver.send(
        QueryInstanceType(device=DeviceShort(0), instance=InstanceNumber(0))
    )

    assert isinstance(response, NumericResponse)
    assert response.value == "(missing)"
    assert check_bad_rsp(response)


@pytest.mark.asyncio
async def test_reset_dali_response_drains_all_without_critical(caplog):
    """Stale buffered responses must all be cleared and not logged as CRITICAL.

    A late backward frame that missed its query is routine on a busy bus; the
    old code discarded only one item and logged it at CRITICAL, spamming logs.
    """
    protocol = DriverLubaRs232.LubaProtocol()
    protocol._queue_rx_raw_dali.put_nowait(6)
    protocol._queue_rx_raw_dali.put_nowait(7)
    protocol._queue_rx_raw_dali.put_nowait(8)

    with caplog.at_level(logging.DEBUG, logger="dali.driver"):
        protocol.reset_dali_response()

    assert protocol._queue_rx_raw_dali.empty()
    assert not [r for r in caplog.records if r.levelno >= logging.CRITICAL]
    assert any("discarded 3 stale" in r.getMessage() for r in caplog.records)


def _connecting_driver(monkeypatch, info_side_effect):
    """Return a driver whose transport is faked and handshake is scripted."""
    driver = DriverLubaRs232("luba232:/dev/ttyACM0")
    protocol = MagicMock()
    connected = asyncio.Event()
    connected.set()
    protocol.connected = connected
    protocol.send_device_info_query = AsyncMock(side_effect=info_side_effect)
    protocol.send_device_settings = AsyncMock()
    protocol.reset_luba_response = MagicMock()
    monkeypatch.setattr(
        "dali.driver.serial.serialx.create_serial_connection",
        AsyncMock(return_value=(MagicMock(), protocol)),
    )
    return driver, protocol


@pytest.mark.asyncio
async def test_connect_retries_handshake_on_timeout(monkeypatch):
    """A busy bus can time out the first handshake frames; connect must retry.

    The interface is slow to acknowledge the info/settings exchange while a
    device streams events, so a single timeout should not fail the connect.
    """
    driver, protocol = _connecting_driver(
        monkeypatch, [asyncio.TimeoutError, asyncio.TimeoutError, None]
    )

    await driver.connect()

    assert driver.is_connected
    assert protocol.send_device_info_query.await_count == 3
    assert protocol.send_device_settings.await_count == 1
    assert protocol.reset_luba_response.call_count == 2


@pytest.mark.asyncio
async def test_connect_raises_after_exhausting_handshake_attempts(monkeypatch):
    """When every handshake attempt times out, connect must give up and raise."""
    driver, protocol = _connecting_driver(monkeypatch, asyncio.TimeoutError)

    with pytest.raises(asyncio.TimeoutError):
        await driver.connect()

    assert not driver.is_connected
    attempts = DriverLubaRs232.handshake_attempts
    assert protocol.send_device_info_query.await_count == attempts
    assert protocol.reset_luba_response.call_count == attempts - 1


@pytest.mark.asyncio
async def test_reset_luba_response_drains_all(caplog):
    """Stale LUBA command replies must be cleared before a handshake retry."""
    protocol = DriverLubaRs232.LubaProtocol()
    protocol._queue_rx_luba_cmd.put_nowait("stale-1")
    protocol._queue_rx_luba_cmd.put_nowait("stale-2")

    protocol.reset_luba_response()

    assert protocol._queue_rx_luba_cmd.empty()
