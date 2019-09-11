class Email(object):
    def __init__(self, fromAddress, to, subject, message):
        self.fromAddress = fromAddress
        self.to = to
        self.subject = subject
        self.message = message
