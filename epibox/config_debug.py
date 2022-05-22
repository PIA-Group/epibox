class Flags:
    """
    Class debug
    """

    def __init__(self):

        self.debug = False


def log(message):
    """
    config_debug.logs a message only if debug is true
    """
    flag = Flags()
    if flag.debug:
        print(message)
