class ConnectionErrorBase(Exception):
    pass


class DataErrorBase(Exception):
    pass


class DetectorConnectionError(ConnectionErrorBase):
    pass


class DetectorDataError(DataErrorBase):
    pass


class TranslatorConnectionError(ConnectionErrorBase):
    pass


class TranslatorDataError(DataErrorBase):
    pass
