class Error(Exception):
    """Base class for other exceptions"""

    pass


class MQTTConnectionError(Error):
    """Client is not currently connected."""

    pass


class DeviceConnectionTimeout(Error):
    """Timeout while attempting to connect to device."""

    pass


class StorageTimeout(Error):
    """Timeout while looking for storage."""

    pass


class BITalinoParameterError(Error):
    """Error raised while connecting to BITalino device due to invalid parameters."""

    pass


class ScientISSTConnectionError(Error):
    """Error raised while connecting to ScientISST device due to loss of comnmunication."""

    pass


class ScientISSTNotFound(Error):
    """ScientISST device not paired."""

    pass


class DeviceNotInAcquisitionError(Error):
    """Device not in acquisition."""

    pass


class DeviceNotIDLEError(Error):
    """Device not IDLE."""

    pass


class PlatformNotSupportedError(Error):
    """Platform not supported"""

    pass
