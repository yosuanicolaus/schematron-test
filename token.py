class AbstractToken:
    def __str__(self):
        # TO BE OVERRIDDEN
        return ""


class CaptureToken(AbstractToken):

    def __str__(self):
        return f"</{self.tag_name}>"


class OpeningTagToken(AbstractToken):
    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    def __str__(self):
        return f"<{self.tag_name}>"


class ClosingTagToken(AbstractToken):
    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    def __str__(self):
        return f"</{self.tag_name}>"
