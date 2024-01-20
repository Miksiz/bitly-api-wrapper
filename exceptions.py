class APIException(BaseException):
  pass

class APIConnectionError(APIException):
  pass

class APILimitsError(APIException):
  pass