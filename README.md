# Python XSLT2 Schematron Validator

Why: `elementpath` is slow.

References:

- [Python XPath 2.0 with elementpath](https://medium.com/@eric.websmith/python-xpath-2-0-with-elementpath-b31176e1fe4f)
- [Convert XML to dictionary](https://gist.github.com/jacobian/795571)
- [Writing a tokenizer for interpreter/compiler](https://docs.python.org/3/library/re.html#writing-a-tokenizer) and
  [some parsing tool](https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html)

- [regex in xpath using re:match (need namespace)](https://stackoverflow.com/a/2756994/17859248)

For `some $foo in $listvals satisfies $foo = @someelem`, one idea with [contains](https://stackoverflow.com/a/3025957/17859248)
