from parser_tree import ParserTree


class Parser:
    def __init__(self, patterns):
        self.patterns = patterns
        self.tokenTree = ParserTree(patterns)

    def parse(self, text):
        pass
