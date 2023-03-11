class AkashicRecordsError(Exception):
    pass


class ExhaustedAttemtpsError(AkashicRecordsError):
    pass


class MultiError(AkashicRecordsError):
    def __init__(self, initial=None):
        super().__init__("Multiple errors occured")
        self.errors = [] if not initial else [initial]

    def append(self, error):
        self.errors.append(error)
