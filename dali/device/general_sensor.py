"""Commands and events from IEC 62386 part 306: General sensors."""

from enum import IntEnum

from dali import command
from dali.device import general

# IEC 62386-306 instance type.
instance_type = 6


class MeasurementVariable(IntEnum):
    """DTR0 values for QUERY MEASUREMENT VARIABLE, from Part 306 Table 17."""

    ALARM_IS_ACTIVATED = 0x00
    ALARM_TYPE = 0x01
    INPUT_SIGNAL_SIGNED = 0x02
    ALARM_0_BYTE_0 = 0x03
    ALARM_0_BYTE_1 = 0x04
    ALARM_0_BYTE_2 = 0x05
    ALARM_1_BYTE_0 = 0x06
    ALARM_1_BYTE_1 = 0x07
    ALARM_1_BYTE_2 = 0x08
    ALARM_2_BYTE_0 = 0x09
    ALARM_2_BYTE_1 = 0x0A
    ALARM_2_BYTE_2 = 0x0B
    ALARM_3_BYTE_0 = 0x0C
    ALARM_3_BYTE_1 = 0x0D
    ALARM_3_BYTE_2 = 0x0E
    ALARM_0_HYSTERESIS_BYTE_0 = 0x0F
    ALARM_0_HYSTERESIS_BYTE_1 = 0x10
    ALARM_0_HYSTERESIS_BYTE_2 = 0x11
    ALARM_1_HYSTERESIS_BYTE_0 = 0x12
    ALARM_1_HYSTERESIS_BYTE_1 = 0x13
    ALARM_1_HYSTERESIS_BYTE_2 = 0x14
    ALARM_2_HYSTERESIS_BYTE_0 = 0x15
    ALARM_2_HYSTERESIS_BYTE_1 = 0x16
    ALARM_2_HYSTERESIS_BYTE_2 = 0x17
    ALARM_3_HYSTERESIS_BYTE_0 = 0x18
    ALARM_3_HYSTERESIS_BYTE_1 = 0x19
    ALARM_3_HYSTERESIS_BYTE_2 = 0x1A
    UNIT_OF_MEASUREMENT = 0x1B
    UNIT_OF_MEASUREMENT_EXTENDED_0 = 0x1C
    UNIT_OF_MEASUREMENT_EXTENDED_1 = 0x1D
    QUANTITY_NAME = 0x1E
    QUANTITY_NAME_EXTENDED_0 = 0x1F
    QUANTITY_NAME_EXTENDED_1 = 0x20
    MAGNITUDE = 0x21
    MAGNITUDE_PHYSICAL_MAX = 0x22
    MAGNITUDE_PHYSICAL_MIN = 0x23
    MAX_INPUT_VALUE_BYTE_0 = 0x24
    MAX_INPUT_VALUE_BYTE_1 = 0x25
    MAX_INPUT_VALUE_BYTE_2 = 0x26
    MAX_INPUT_VALUE_BYTE_3 = 0x27
    MIN_INPUT_VALUE_BYTE_0 = 0x28
    MIN_INPUT_VALUE_BYTE_1 = 0x29
    MIN_INPUT_VALUE_BYTE_2 = 0x2A
    MIN_INPUT_VALUE_BYTE_3 = 0x2B


class UnitOfMeasurement(IntEnum):
    """Standard unit-of-measurement values from Part 306 Annex A, Table 18."""

    MANUFACTURER_DEFINED = 0
    DIMENSIONLESS = 1
    SECOND = 2
    HERTZ = 3
    METRE = 4
    KILOGRAM = 5
    VOLT = 6
    AMPERE = 7
    KELVIN = 8
    CELSIUS = 9
    FAHRENHEIT = 10
    MOLE = 11
    RAD = 13
    STERADIAN = 14
    NEWTON = 15
    PASCAL = 16
    PSI = 17
    JOULE = 18
    WATT = 19
    COULOMB = 20
    FARAD = 21
    OHM = 22
    SIEMENS = 23
    WEBER = 24
    TESLA = 25
    HENRY = 26
    AMPERE_PER_METRE = 27
    VOLTS_PER_METRE = 28
    LUMEN = 31
    LUX = 32
    CANDELA = 33
    CANDELA_PER_SQUARE_METRE = 34
    BECQUEREL = 36
    GRAY = 37
    SIEVERT = 38
    KATAL = 39
    SQUARE_METRE = 41
    CUBIC_METRE = 42
    METRE_PER_SECOND = 43
    METRE_PER_SECOND_SQUARED = 44
    CUBIC_METRE_PER_SECOND = 45
    KILOGRAM_PER_CUBIC_METRE = 46
    KILOGRAM_PER_SQUARE_METRE = 47
    CUBIC_METRE_PER_KILOGRAM = 48
    FEET = 49
    NEWTON_METRE = 51
    POSITION_COORDINATE = 53
    DECIBEL = 55
    PERCENT = 56
    PART_PER_THOUSAND = 57
    PART_PER_TEN_THOUSAND = 58
    PARTS_PER_MILLION = 59


class QuantityName(IntEnum):
    """Standard quantity-name values from Part 306 Annex A, Table 19."""

    MANUFACTURER_DEFINED = 0
    TIME = 1
    FREQUENCY = 2
    LENGTH = 4
    FORCE = 5
    WEIGHT = 6
    MASS = 7
    VELOCITY = 8
    AREA = 9
    VOLUME = 10
    TORQUE = 11
    VOLTAGE = 13
    CURRENT = 14
    POWER = 15
    POWER_APPARENT = 16
    POWER_REACTIVE = 17
    ENERGY = 18
    POWER_FACTOR = 19
    SOUND_PRESSURE_LEVEL = 20
    CCT = 22
    CRI = 23
    RED_LIGHT = 24
    GREEN_LIGHT = 25
    BLUE_LIGHT = 26
    TEMPERATURE = 27
    WET_BULB_TEMPERATURE = 28
    ABSOLUTE_HUMIDITY = 29
    RELATIVE_HUMIDITY = 30
    DEW_POINT = 31
    PRESSURE = 32
    FLOW_RATE = 33
    CO2 = 35
    CO = 36
    VOC = 37
    NO2 = 38
    AMMONIA = 39
    PARTICULATE_MATTER_PM10 = 41
    PARTICULATE_MATTER_PM2_5 = 42
    AIR_QUALITY_INDEX = 43
    RSSI_IBEACON = 44
    RSSI_EDDYSTONE = 45
    RSSI_ALTBEACON = 46
    GLOBAL_POSITION = 47
    RELATIVE_POSITION = 48
    ALTITUDE = 49


class GeneralSensorEvent(general._Event):
    """A Part 306 measured-value event."""

    _instance_type = instance_type
    _event_info = 0x20000

    @classmethod
    def from_event_data(cls, event_data: int):
        """Return this event class for a measurement event."""
        return cls if event_data & 0x200 else None

    @property
    def measured_value(self) -> int:
        """Return the 9-bit measured-value event payload."""
        return self.event_data & 0x1FF

    @property
    def event_data(self) -> int:
        """Return the encoded event information."""
        return self._event_info

    def _set_event_data(self, set_data: int, set_frame) -> None:
        """Encode the measured value into a Part 306 event frame."""
        if not isinstance(set_data, int) or not 0 <= set_data <= 0x3FF:
            raise ValueError("GeneralSensorEvent requires 9-bit event data")
        self._event_info = 0x200 | (set_data & 0x1FF)
        set_frame[9:0] = self._event_info


class InstanceEventFilter(general.InstanceEventFilter):
    """Part 306 event filters."""

    measured_value = 0x01


class QueryMeasurementVariable(general._StandardInstanceCommand):
    """Query a Part 306 measurement variable selected by DTR0."""

    inputdev = True
    uses_dtr0 = True
    response = command.NumericResponse
    _opcode = 0x5F
