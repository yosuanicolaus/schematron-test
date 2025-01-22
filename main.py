import elementpath
import ipdb
import re

from lxml import etree
from lxml.etree import _Element
from rich.pretty import pprint
from time import time
from typing import List, Optional, Tuple


parser = elementpath.XPath2Parser
parser.DEFAULT_NAMESPACES.update({"u": "utils"})
rcr = 0
rce = 0


def print_time(name: str, start_time: float, force=False):
    """
    To be used like:

    if print_time("funcname", tt):
        # potentially run debugger here
        pass

    :return: if True, the time spent is "significant"
    """
    finish_time = time()
    total_time = finish_time - start_time

    if force or total_time > 0.05:  # significant
        # print(f"timed {name}: {total_time} (rcr={rcr})")
        return True

    return False


@parser.method(
    parser.function(
        "gln", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
def evaluate_gln_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(
        num * (1 + (((index + 1) % 2) * 2))
        for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1])
    )
    return (10 - (weighted_sum % 10)) % 10 == int(val[-1])


@parser.method(
    parser.function(
        "slack",
        prefix="u",
        nargs=3,
        sequence_types=("xs:decimal", "xs:decimal", "xs:decimal", "xs:boolean"),
    )
)
def evaluate_slack_function(self, context=None):
    exp = self.get_argument(context, default="", cls=elementpath.datatypes.Decimal)
    val = self.get_argument(
        context, index=1, default="", cls=elementpath.datatypes.Decimal
    )
    slack = self.get_argument(
        context, index=2, default="", cls=elementpath.datatypes.Decimal
    )
    return (exp + slack) >= val and (exp - slack) <= val


@parser.method(
    parser.function(
        "mod11", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
def evaluate_mod11_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(
        num * ((index % 6) + 2)
        for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1])
    )
    return int(val) > 0 and (11 - (weighted_sum % 11)) % 11 == int(val[-1])


@parser.method(
    parser.function(
        "mod97-0208", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
def evaluate_mod97_0208_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)[2:]
    return int(val[-2:]) == 97 - (int(val[:-2]) % 97)


@parser.method(
    parser.function(
        "checkCodiceIPA",
        prefix="u",
        nargs=1,
        sequence_types=("xs:string?", "xs:boolean"),
    )
)
def evaluate_checkCodiceIPA_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    return bool(len(val) == 6 and re.match("^[a-zA-Z0-9]+$", val))


@parser.method(
    parser.function(
        "checkCF", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
@parser.method(
    parser.function(
        "checkCF16", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
def evaluate_checkCF_function(self, context=None):
    """Check the characters of the codice fiscale to ensure it conforms to either the 16 or 11 character standards"""
    val = self.get_argument(context, default="", cls=str)
    if self.symbol == "checkCF16" or len(val) == 16:
        return bool(
            re.fullmatch(r"[a-zA-Z]{6}\d{2}[a-zA-Z]\d{2}[a-zA-Z\d]{3}\d[a-zA-Z]", val)
        )
    elif len(val) == 11:
        return val.isnumeric()

    return False


@parser.method(
    parser.function(
        "checkPIVA", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")
    )
)
@parser.method(
    parser.function(
        "addPIVA",
        prefix="u",
        nargs=2,
        sequence_types=("xs:string", "xs:integer", "xs:integer"),
    )
)
@parser.method(
    parser.function(
        "checkPIVAseIT", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")
    )
)
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


@parser.method(
    parser.function(
        "abn", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")
    )
)
def evaluate_abn_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    subtractors = [49] + [48] * 10
    multipliers = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return bool(
        sum(
            (ord(character) - subtractors[index]) * multipliers[index]
            for index, character in enumerate(val)
        )
        % 89
        == 0
    )


@parser.method(
    parser.function(
        "TinVerification",
        prefix="u",
        nargs=1,
        sequence_types=("xs:string", "xs:boolean"),
    )
)
def evaluate_TinVerification_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    return sum(
        int(character) * (2 ** (index + 1))
        for index, character in enumerate(val[:8][::-1])
    ) % 11 % 10 == int(val[-1])


class Element:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self._children = []
        self._variables = []
        self._parent = None

    def set_variable(self, name, path):
        self._variables.append(
            (
                name,
                elementpath.Selector(path, namespaces=self.namespaces, parser=parser),
            )
        )

    @property
    def variables(self):
        if not self._parent:
            return self._variables
        return self._parent.variables + self._variables

    def run(self, xml, variables_dict: Optional[dict] = None):
        """Evaluate the variables at the current level, and then run the children."""
        global rce
        rce += 1
        evaluated_variables = variables_dict and variables_dict.copy() or {}
        for name, selector in self._variables:
            evaluated_variables.update(
                {name: selector.select(xml, variables=evaluated_variables)}
            )

        warning, fatal = [], []
        if self._children:
            for child in self._children:
                res_warning, res_fatal = child.run(
                    xml, variables_dict=evaluated_variables
                )
                warning += res_warning
                fatal += res_fatal

        return warning, fatal


class ElementSchematron(Element):
    @classmethod
    def from_sch(cls, sch: _Element):
        tt = time()

        def set_vars(element, node):
            """Updates the given element object with the variables local
            to the particular node it corresponds to.
            """
            for var in node.findall("./let", namespaces=sch_namespace):
                element.set_variable(var.get("name"), var.get("value"))

        # This is the namespace used to interpret the sch file
        sch_namespace = {"": "http://purl.oclc.org/dsdl/schematron"}

        # Generate the namespaces used to interpet the documents to be validated
        namespace_dict = {}
        for ns in sch.findall("./ns", namespaces=sch_namespace):
            namespace_dict.update({ns.get("prefix"): ns.get("uri")})

        schematron = cls(namespaces=namespace_dict)
        set_vars(schematron, sch)
        for pattern_node in sch.findall("./pattern", namespaces=sch_namespace):
            pattern = schematron.add_element_pattern(pattern_node.get("id") or "")
            set_vars(pattern, pattern_node)
            for rule_node in pattern_node.findall("./rule", namespaces=sch_namespace):
                rule = pattern.add_element_rule(rule_node.get("context"))
                set_vars(rule, rule_node)
                for assertion in rule_node.findall(
                    "./assert", namespaces=sch_namespace
                ):
                    rule.add_assert(
                        assertion.get("id"),
                        assertion.get("flag"),
                        assertion.get("test"),
                        assertion.text,
                    )

        # print_time("Schematron.from_sch", tt)
        return schematron

    def __init__(
        self, namespaces: Optional[dict] = None, parent: Optional[Element] = None
    ):
        self.namespaces = namespaces
        self._parent = parent

        self._children: List[ElementPattern] = []
        self._variables = []

    def add_element_pattern(self, pattern_id=""):
        self._children.append(ElementPattern(pattern_id, self.namespaces, self))
        return self._children[-1]


class ElementPattern(Element):
    def __init__(
        self,
        pattern_id="",
        namespaces: Optional[dict] = None,
        parent: Optional[ElementSchematron] = None,
    ):
        self.pattern_id = pattern_id
        self.namespaces = namespaces
        self._parent = parent

        self._children: List[ElementRule] = []
        self._variables = []

    def add_element_rule(self, context):
        self._children.append(
            ElementRule(context, namespaces=self.namespaces, parent=self)
        )
        return self._children[-1]


class ElementRule(Element):
    def __init__(
        self,
        context,
        namespaces: Optional[dict] = None,
        parent: Optional[ElementPattern] = None,
    ):
        split_context = context.split("|")
        for i, or_context in enumerate(split_context):
            or_context = or_context.strip()
            if not or_context.startswith("/"):
                split_context[i] = f"//{or_context}"
        context = " | ".join(split_context)

        self._parent = parent
        self.namespaces = namespaces

        self._variables: List[Tuple[str, elementpath.Selector]] = []

        self.context_selector = elementpath.Selector(
            context, namespaces=self.namespaces, parser=parser
        )
        self._assertions: List[
            Tuple[str, str, elementpath.Selector, str]
        ] = []  # list of 4 element tuples, consisting of assert_id, flag, test (selector), message

    def run(self, xml, variables_dict=None):
        """This overides the Element run function"""
        global rcr
        tt = time()
        rcr += 1
        totvar = 0
        totasr = 0

        context_nodes = self.context_selector.select(xml, variables=variables_dict)
        warning, fatal = [], []
        for context_node in context_nodes:
            # Then evaluate the variables at this level
            evaluated_variables = variables_dict and variables_dict.copy() or {}

            t2 = time()
            for name, selector in self._variables:
                evaluated_variables.update(
                    {
                        name: selector.select(
                            xml, item=context_node, variables=evaluated_variables
                        )
                    }
                )

            if rcr == 14:
                # print_time("update evaluated_variables", t2, force=True)
                totvar += time() - t2
                # pprint(evaluated_variables)

            t2 = time()
            # Run every assertion
            for assert_id, flag, selector, message in self._assertions:
                res = selector.select(
                    context_node,
                    variables=evaluated_variables,
                )
                if not res:
                    if flag == "warning":
                        warning.append(f"[{assert_id}] {message}")
                    elif flag == "fatal":
                        fatal.append(f"[{assert_id}] {message}")
                        # ipdb.set_trace()

            if rcr == 14:
                # print_time("run assertion             ", t2, force=True)
                totasr += time() - t2

        if print_time("Rule.run", tt):
            # ipdb.set_trace()
            pass

        if rcr == 14:
            pass
            # pprint((totvar, totasr))
            # ipdb.set_trace()
        return warning, fatal

    def add_assert(self, assert_id, flag, test, message):
        self._assertions.append(
            (
                assert_id,
                flag,
                elementpath.Selector(test, namespaces=self.namespaces, parser=parser),
                message,
            )
        )


PEPPOL_PATH = "validation/schematron/PEPPOL-EN16931-UBL.sch"
CEN_PATH = "validation/schematron/PEPPOL-EN16931-UBL.sch"
TEST_FILE_PATH = "INV_2024_00272_ubl_bis3.xml"


def main():
    tta = time()

    peppol_schematron = ElementSchematron.from_sch(etree.parse(PEPPOL_PATH).getroot())
    cen_schematron = ElementSchematron.from_sch(etree.parse(CEN_PATH).getroot())
    doc = etree.parse(TEST_FILE_PATH).getroot()

    warning_out, fatal_out = [], []
    for schematron in (cen_schematron, peppol_schematron):
        warning, fatal = schematron.run(doc)
        warning_out += warning
        fatal_out += fatal

    if warning_out:
        print("Warning:")
        pprint(warning_out)
    if fatal_out:
        print("Fatal:")
        pprint(fatal_out)

    pprint(time() - tta)
    print("rcr:", rcr)
    print("rce:", rce)


main()
