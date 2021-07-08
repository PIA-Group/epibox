class InvalidAddressError(Exception):
    def __init__(self):
        super().__init__("The specified address is invalid.")


class BTAdapterNotFoundError(Exception):
    def __init__(self):
        super().__init__("No Bluetooth adapter was found.")


class DeviceNotFoundError(Exception):
    def __init__(self):
        super().__init__("The device could not be found.")


class ContactingDeviceError(Exception):
    def __init__(self):
        super().__init__("The computer lost communication with the device.")


class PortCouldNotBeOpenedError(Exception):
    def __init__(self):
        super().__init__(
            "The communication port does not exist or it is already being used."
        )


class PortInitializationError(Exception):
    def __init__(self):
        super().__init__("The communication port could not be initialized.")


class DeviceNotIdleError(Exception):
    def __init__(self):
        super().__init__("The device is not idle.")


class DeviceNotInAcquisitionError(Exception):
    def __init__(self):
        super().__init__("The device is not in acquisition mode.")


class InvalidParameterError(Exception):
    def __init__(self):
        super().__init__("Invalid parameter.")


class NotSupportedError(Exception):
    def __init__(self):
        super().__init__("Operation not supported by the device.")


class UnknownError(Exception):
    def __init__(self, message=""):
        super().__init__("Unknown error. ".format(message))