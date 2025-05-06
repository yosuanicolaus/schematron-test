import re
import sys
from time import time

import elementpath
from elementpath.xpath3 import XPath3Parser
from lxml import etree
from rich.pretty import pprint

from myconst import get_file_and_schematron_paths

# This parser is modified to be able to add the functions
custom_parser = elementpath.XPath2Parser
custom_parser.DEFAULT_NAMESPACES.update({"u": "utils"})
method = custom_parser.method
function = custom_parser.function


@method(function("gln", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_gln_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(num * (1 + (((index + 1) % 2) * 2)) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return (10 - (weighted_sum % 10)) % 10 == int(val[-1])


@method(function("slack", prefix="u", nargs=3, sequence_types=("xs:decimal", "xs:decimal", "xs:decimal", "xs:boolean")))
def evaluate_slack_function(self, context=None):
    exp = self.get_argument(context, default="", cls=elementpath.datatypes.Decimal)
    val = self.get_argument(context, index=1, default="", cls=elementpath.datatypes.Decimal)
    slack = self.get_argument(context, index=2, default="", cls=elementpath.datatypes.Decimal)
    return (exp + slack) >= val and (exp - slack) <= val


@method(function("mod11", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_mod11_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(num * ((index % 6) + 2) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return int(val) > 0 and (11 - (weighted_sum % 11)) % 11 == int(val[-1])


@method(function("mod97-0208", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_mod97_0208_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)[2:]
    return int(val[-2:]) == 97 - (int(val[:-2]) % 97)


@method(function("checkCodiceIPA", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_checkCodiceIPA_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    return bool(len(val) == 6 and re.match("^[a-zA-Z0-9]+$", val))


@method(function("checkCF", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
@method(function("checkCF16", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_checkCF_function(self, context=None):
    """Check the characters of the codice fiscale to ensure it conforms to either the 16 or 11 character standards"""
    val = self.get_argument(context, default="", cls=str)
    if self.symbol == "checkCF16" or len(val) == 16:
        return bool(re.fullmatch(r"[a-zA-Z]{6}\d{2}[a-zA-Z]\d{2}[a-zA-Z\d]{3}\d[a-zA-Z]", val))
    elif len(val) == 11:
        return val.isnumeric()

    return False


@method(function("checkPIVA", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
@method(function("addPIVA", prefix="u", nargs=2, sequence_types=("xs:string", "xs:integer", "xs:integer")))
@method(function("checkPIVAseIT", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
def evaluate_checkPIVA_function(self, context=None):
    """Recursive implementation of a version of the luhn 10 algorithm used for checking partita IVA

    The checksum is valid when the resultant value mod 10 is zero
    """
    CHECK_NO = "0246813579"

    def addPIVA(arg, pari):
        # Because of the way the xpath substr function works, the base case is arg as an empty string
        # pari is used to alterate, such that the CHECK_NO is indexed every other character
        if not arg.isnumeric():
            return 0
        else:
            if pari:
                return int(CHECK_NO[int(arg[0])]) + addPIVA(arg[1:], not pari)
            else:
                return int(arg[0]) + addPIVA(arg[1:], not pari)

    if self.symbol == "checkPIVA":
        val = self.get_argument(context, default="", cls=str)
        if not val.isnumeric:
            return 1
        return addPIVA(val, False) % 10

    elif self.symbol == "addPIVA":
        arg = self.get_argument(context, default="", cls=str)
        pari = self.get_argument(context, index=1, default="", cls=int)
        return addPIVA(arg, pari)

    elif self.symbol == "checkPIVAseIT":
        val = self.get_argument(context, default="", cls=str)
        if val[:2].upper() != "IT" or len(val) != 13:
            return False
        else:
            return bool(addPIVA(val[2:], False) % 10 == 0)

    return False


@method(function("abn", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_abn_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    subtractors = [49] + [48] * 10
    multipliers = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return bool(sum((ord(character) - subtractors[index]) * multipliers[index] for index, character in enumerate(val)) % 89 == 0)


@method(function("TinVerification", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
def evaluate_TinVerification_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    return sum(int(character) * (2 ** (index + 1)) for index, character in enumerate(val[:8][::-1])) % 11 % 10 == int(val[-1])


class Element:
    def __init__(self, namespaces, parser=None):
        self.namespaces = namespaces
        self.parser = parser

    def set_variable(self, name, path):
        self._variables.append((name, elementpath.Selector(path, namespaces=self.namespaces, parser=self.parser)))

    @property
    def variables(self):
        if not self._parent:
            return self._variables
        return self._parent.variables + self._variables

    def run(self, xml, variables_dict=None):
        # Evaluate the variables at the current level, and then run the children
        evaluated_variables = variables_dict and variables_dict.copy() or {}
        for name, selector in self._variables:
            evaluated_variables.update({name: selector.select(xml, variables=evaluated_variables)})

        warning, fatal = [], []
        if self._children:
            for child in self._children:
                res_warning, res_fatal = child.run(xml, variables_dict=evaluated_variables)
                warning += res_warning
                fatal += res_fatal
        return warning, fatal


class Schematron(Element):
    @classmethod
    def from_sch(cls, sch, parser=custom_parser):
        def set_vars(element, node, namespace):
            """Updates the given element object with the variables local
            to the particular node it corresponds to.
            """
            var_nodes = (
                node.findall("./let", namespaces=sch_namespace)
                if "xsl" not in namespace
                else node.xpath("./xsl:variable | ./sch:let", namespaces=namespace)
            )
            for var in var_nodes:
                if "xsl" == var.prefix:
                    value = ""
                    choice_node = var.find("./xsl:choose", namespaces=namespace)
                    for choice in choice_node:
                        child = choice.find("./xsl:value-of", namespaces=namespace)
                        node_text = child.attrib.get("select") if child is not None else choice.text
                        if choice.attrib.get("test"):
                            value = f"if({choice.attrib['test']}) then {node_text} else {value}"
                        else:
                            value = f"{value} {node_text}"
                    element.set_variable(var.get("name"), value)
                else:
                    element.set_variable(var.get("name"), var.get("value"))

        # This is the namespace used to interpret the sch file
        sch_namespace = {None: "http://purl.oclc.org/dsdl/schematron"}

        # Generate the namespaces used to interpet the documents to be validated
        namespace_dict = {"sch": "http://purl.oclc.org/dsdl/schematron"}
        for ns in sch.findall("./ns", namespaces=sch_namespace):
            namespace_dict.update({ns.get("prefix"): ns.get("uri")})
        schematron = cls(namespaces=namespace_dict, parser=parser)
        set_vars(schematron, sch, namespace_dict)
        for pattern_node in sch.findall("./pattern", namespaces=sch_namespace):
            pattern = schematron.pattern(pattern_node.get("id"))
            set_vars(pattern, pattern_node, namespace_dict)
            for rule_node in pattern_node.findall("./rule", namespaces=sch_namespace):
                rule = pattern.rule(rule_node.get("context"))
                set_vars(rule, rule_node, namespace_dict)
                for assertion in rule_node.findall("./assert", namespaces=sch_namespace):
                    rule._assert(assertion.get("id"), assertion.get("flag"), assertion.get("test"), assertion.text)
        return schematron

    def __init__(self, namespaces=None, parent=None, parser=None):
        self.namespaces = namespaces
        self._parent = parent
        self.parser = parser

        self._children = []
        self._variables = []
        self._functions = []

    def pattern(self, pattern_id=""):
        self._children.append(Pattern(pattern_id, self.namespaces, self))
        return self._children[-1]


class Pattern(Element):
    def __init__(self, pattern_id="", namespaces=None, parent=None):
        self.pattern_id = pattern_id
        self.namespaces = namespaces
        self.parser = parent and parent.parser
        self._parent = parent

        self._children = []
        self._variables = []
        self._functions = []

    def rule(self, context):
        self._children.append(Rule(context, parent=self, namespaces=self.namespaces))
        return self._children[-1]


class Rule(Element):
    def __init__(self, context, namespaces=None, parent=None):
        self.context = context
        self._parent = parent
        self.namespaces = namespaces
        self.parser = parent and parent.parser

        self._variables = []
        self._functions = []

        self.context_selector = elementpath.Selector(self.context, namespaces=self.namespaces, parser=self.parser)
        self._assertions = []  # list of 4 element tuples, consisting of assert_id, flag, test (selector), message

    def run(self, xml, variables_dict=None):
        """This overides the Element run function"""
        context_nodes = self.context_selector.select(xml, variables=variables_dict)
        warning, fatal = [], []
        for context_node in context_nodes:
            # Then evaluate the variables at this level
            evaluated_variables = variables_dict and variables_dict.copy() or {}
            for name, selector in self._variables:
                evaluated_variables.update({name: selector.select(xml, item=context_node, variables=evaluated_variables)})

            # Run every assertion
            for assert_id, flag, selector, message in self._assertions:
                res = selector.select(xml, item=context_node, variables=evaluated_variables)
                if not res:
                    if flag == "warning":
                        warning.append(f"[{assert_id}] {message}")
                    elif flag == "fatal":
                        fatal.append(f"[{assert_id}] {message}")
        return warning, fatal

    def _assert(self, assert_id, flag, test, message):
        self._assertions.append((assert_id, flag, elementpath.Selector(test, namespaces=self.namespaces, parser=self.parser), message))


def main():
    tta = time()
    test_file_path, schematron_paths = get_file_and_schematron_paths(sys.argv[1:])

    for schematron_path in schematron_paths:
        print(f"Running {schematron_path}")
        schematron = Schematron.from_sch(etree.parse(schematron_path).getroot(), parser=XPath3Parser)
        doc = etree.parse(test_file_path).getroot()
        warning, fatal = schematron.run(doc)
        if warning:
            print("Warning:")
            pprint(warning)
        if fatal:
            print("Fatal:")
            pprint(fatal)

    pprint(time() - tta)


if __name__ == "__main__":
    main()
