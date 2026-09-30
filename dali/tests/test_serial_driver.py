import asyncio
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
