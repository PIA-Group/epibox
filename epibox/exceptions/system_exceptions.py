
class Error(Exception):
   """Base class for other exceptions"""
   pass


class ConnectionBad(Error):
   """Raised when the input value is too small"""
   pass
