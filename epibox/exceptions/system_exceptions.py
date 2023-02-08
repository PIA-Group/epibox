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


class DeviceNotInAcquisitionError(Error):
    """Device not in acquisition."""

    pass


class DeviceNotIDLEError(Error):
    """Device not IDLE."""

    pass
