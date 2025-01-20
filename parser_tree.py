class ParserTreeLeaf:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def add_in_chain(self, c):
        return self.values.setdefault(c, ParserTreeLeaf())

    def add_token(self, c, token):
        self.values[c] = token


class ParserTree:
    def __init__(self, patterns):
        self.root = ParserTreeLeaf()
        for pattern in patterns:
            for token in pattern.tokens:
                node = self.root
                token_str = str(token)
                for i, c in enumerate(token_str):
                    if i == len(token_str) - 1:
                        node.add_token(token)
                    else:
                        node = node.add_in_chain(c)
