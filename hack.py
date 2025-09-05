import re
import sys
from copy import deepcopy
from time import time
from typing import Generic, List, Optional, Tuple, TypeVar

import elementpath
from lxml import etree
from lxml.etree import _Element
from rich.pretty import pprint

from .schematron_lxml_const import INVOICE_LINE_TAG, PATH_ROOT_MAP, TEST_MAP

parser = elementpath.XPath2Parser
parser.DEFAULT_NAMESPACES.update({"u": "utils"})
rcr = 0
rce = 0
T = TypeVar("T", bound="Element")


################################################################################
# Parser Functions
################################################################################


@parser.method(parser.function("gln", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_gln_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(num * (1 + (((index + 1) % 2) * 2)) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return (10 - (weighted_sum % 10)) % 10 == int(val[-1])


@parser.method(parser.function("slack", prefix="u", nargs=3, sequence_types=("xs:decimal", "xs:decimal", "xs:decimal", "xs:boolean")))
def evaluate_slack_function(self, context=None):
    exp = self.get_argument(context, default="", cls=elementpath.datatypes.Decimal)
    val = self.get_argument(context, index=1, default="", cls=elementpath.datatypes.Decimal)
    slack = self.get_argument(context, index=2, default="", cls=elementpath.datatypes.Decimal)
    return (exp + slack) >= val and (exp - slack) <= val


@parser.method(parser.function("mod11", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_mod11_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    weighted_sum = sum(num * ((index % 6) + 2) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return int(val) > 0 and (11 - (weighted_sum % 11)) % 11 == int(val[-1])


@parser.method(parser.function("mod97-0208", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_mod97_0208_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)[2:]
    return int(val[-2:]) == 97 - (int(val[:-2]) % 97)


@parser.method(parser.function("checkCodiceIPA", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_checkCodiceIPA_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    return bool(len(val) == 6 and re.match("^[a-zA-Z0-9]+$", val))


@parser.method(parser.function("checkCF", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
@parser.method(parser.function("checkCF16", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_checkCF_function(self, context=None):
    """Check the characters of the codice fiscale to ensure it conforms to either the 16 or 11 character standards"""
    val = self.get_argument(context, default="", cls=str)
    if self.symbol == "checkCF16" or len(val) == 16:
        return bool(re.fullmatch(r"[a-zA-Z]{6}\d{2}[a-zA-Z]\d{2}[a-zA-Z\d]{3}\d[a-zA-Z]", val))
    elif len(val) == 11:
        return val.isnumeric()

    return False


@parser.method(parser.function("checkPIVA", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
@parser.method(parser.function("addPIVA", prefix="u", nargs=2, sequence_types=("xs:string", "xs:integer", "xs:integer")))
@parser.method(parser.function("checkPIVAseIT", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
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


@parser.method(parser.function("abn", prefix="u", nargs=1, sequence_types=("xs:string?", "xs:boolean")))
def evaluate_abn_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    subtractors = [49] + [48] * 10
    multipliers = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return bool(sum((ord(character) - subtractors[index]) * multipliers[index] for index, character in enumerate(val)) % 89 == 0)


@parser.method(parser.function("TinVerification", prefix="u", nargs=1, sequence_types=("xs:string", "xs:boolean")))
def evaluate_TinVerification_function(self, context=None):
    val = self.get_argument(context, default="", cls=str)
    val = "".join([ch for ch in val if ch.isnumeric()])
    return sum(int(character) * (2 ** (index + 1)) for index, character in enumerate(val[:8][::-1])) % 11 % 10 == int(val[-1])


@parser.method(parser.function("checkSEOrgnr", prefix="u", nargs=1))
def evaluate_checkSEOrgnr_function(self, context=None):
    number = self.get_argument(context, default="", cls=str)

    if not re.match(r"^\d+$", number):
        return False  # Not all digits

    main_part = number[:9]  # First 9 digits
    check_digit = number[9:]  # Last digit

    sum_digits = 0
    for pos in range(1, 10):
        digit = int(main_part[len(main_part) - pos])  # Get digit from right to left
        if pos % 2 == 1:  # Odd position (from right)
            doubled = digit * 2
            sum_digits += (doubled % 10) + (doubled // 10)  # Sum digits of doubled value
        else:  # Even position
            sum_digits += digit

    calculated_check_digit = (10 - sum_digits % 10) % 10

    return calculated_check_digit == int(check_digit)


class Element(Generic[T]):
    def __init__(self, namespaces: dict[str, str], parent: Optional["Element"] = None):
        self.namespaces = namespaces
        self.children: List[T] = []
        self._variables: List[Tuple[str, elementpath.Selector]] = []
        self.parent: Optional[Element] = parent
        self.root_name: Optional[str] = parent and parent.root_name

    def add_variable(self, name, path):
        self._variables.append((name, elementpath.Selector(path, namespaces=self.namespaces, parser=parser)))

    @property
    def variables(self):
        if self.parent:
            return self.parent.variables + self._variables
        else:
            return self._variables

    def run(self, xml, variables_dict: Optional[dict] = None) -> Tuple[List[str], List[str]]:
        """Evaluate the variables at the current level, and then run the children."""
        evaluated_variables = variables_dict and variables_dict.copy() or {}
        for name, selector in self._variables:
            evaluated_variables.update({name: selector.select(xml, variables=evaluated_variables)})

        warning, fatal = [], []
        for child in self.children:
            res_warning, res_fatal = child.run(xml, variables_dict=evaluated_variables)
            warning += res_warning
            fatal += res_fatal

        return warning, fatal


class ElementSchematron(Element):
    def __init__(self, namespaces: dict[str, str], parent: Optional["Element"] = None):
        super().__init__(namespaces, parent)
        self.children: List[ElementPattern] = []

    @classmethod
    def from_sch(cls, sch: _Element, root_name: str):
        """
        Construct the Element tree by traversing the schematron and appending all necessary child elements to their own `children`.
        The Element tree will then look like this:

        ElementSchematron
            ElementPattern
                ElementRule
                ...
            ...
        """

        def add_all_variable(element: Element, node: _Element):
            """
            Updates the given element object with the variables local to the particular node it corresponds to.
            """
            for var in node.findall("./let", namespaces=sch_namespace):
                element.add_variable(var.get("name"), var.get("value"))

        # This is the namespace used to interpret the sch file
        sch_namespace = {"": "http://purl.oclc.org/dsdl/schematron"}

        # Generate the namespaces used to interpet the documents to be validated
        namespace_dict = {}
        for ns in sch.findall("./ns", namespaces=sch_namespace):
            namespace_dict.update({ns.get("prefix"): ns.get("uri")})

        schematron = cls(namespaces=namespace_dict, parent=None)
        schematron.root_name = root_name
        add_all_variable(schematron, sch)

        for pattern_node in sch.findall("./pattern", namespaces=sch_namespace):
            pattern = schematron.add_element_pattern(pattern_node.get("id") or "")
            add_all_variable(pattern, pattern_node)

            for rule_node in pattern_node.findall("./rule", namespaces=sch_namespace):
                rule = pattern.add_element_rule(rule_node.get("context"))
                add_all_variable(rule, rule_node)
                for assertion in rule_node.findall("./assert", namespaces=sch_namespace):
                    rule.add_assert(
                        assertion.get("id"),
                        assertion.get("flag"),
                        assertion.get("test"),
                        assertion.text,
                    )
        return schematron

    def add_element_pattern(self, pattern_id="") -> "ElementPattern":
        self.children.append(ElementPattern(pattern_id, self.namespaces, self))
        return self.children[-1]


class ElementPattern(Element):
    def __init__(self, pattern_id: str, namespaces: dict[str, str], parent: ElementSchematron):
        super().__init__(namespaces=namespaces, parent=parent)
        self.children: List[ElementRule] = []
        self.pattern_id = pattern_id

    def add_element_rule(self, context: str) -> "ElementRule":
        self.children.append(ElementRule(context, namespaces=self.namespaces, parent=self))
        return self.children[-1]


class ElementRule(Element):
    def __init__(self, context: str, namespaces: dict, parent: ElementPattern):
        super().__init__(namespaces=namespaces, parent=parent)
        self.children = []

        # The received `context` string here is in the format of a " | "-separated context items, and
        # each context item will be in the format of "OrphanedNode/AdditionalPathToNode" or "/RootNode/PathToNode".
        # In the first case, we want to prepend them with "//" to explicitly indicate to the Selector
        # that we need to do a find query to that node, because it doesn't start from the root.
        split_context = context.split("|")
        for i, or_context in enumerate(split_context):
            or_context = or_context.strip()
            if not or_context.startswith("/"):
                split_context[i] = f"//{or_context}"
        context = " | ".join(split_context)
        self.context_selector = elementpath.Selector(context, namespaces=self.namespaces, parser=parser)

        # List of 4 element tuples, consisting of assert_id, flag, test (selector), message
        self._assertions: List[Tuple[str, str, elementpath.Selector, str]] = []

    def run(self, xml: _Element, variables_dict: Optional[dict] = None):
        """
        This method overrides Element.run function because ElementRule is at the bottom of the Element tree,
        and it does not have any children.

        Here, we evaluate through all the gathered assertions and variables, and evaluate the XML with some
        strategies to combat the severe performance issues from running elementpath.Selector.select multiple times.
        """
        evaluated_variables = variables_dict and variables_dict.copy() or {}
        context_nodes = self.context_selector.select(xml, variables=variables_dict)
        warning, fatal = [], []

        if self.root_name == "CEN":
            # CEN schematron doesn't have any variable, and evaluate all needed element directly in the selector path.
            # This forces us to evaluate the assertion with the whole XML because it can ask for any element anywhere
            # in the XML at any time, even if they are not related parent-child wise.
            # Fortunately, most of CEN assertion does not depend on every InvoiceLine elements (except some).
            # Hence, the strategy is to create a shallow XML containing all original XML elements EXCEPT the invoice lines.
            # By this approach, the shallow XML to be evaluated will have the size of around 100~200 lines at most.
            # (which is still slow, but much better than the unlimited lines from XML with huge number of invoice lines).
            shallow_xml = deepcopy(xml)
            invoice_line_elements = shallow_xml.xpath(
                _path="//cac:InvoiceLine",
                namespaces={"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"},
            )
            for invoice_line_element in invoice_line_elements:
                shallow_xml.remove(invoice_line_element)
        elif self._variables:
            # For all other schematron, we create a new "shallow" element containing just the root and the context node.
            # And do the expensive select query on this new small XML element instead.
            shallow_xml = deepcopy(xml)
            shallow_xml.clear()
        else:
            shallow_xml = etree.Element("unused")

        for context_node in context_nodes:
            # If the rule has additional variable, we evaluate them here.
            if self._variables:
                evaluated_variables = variables_dict and variables_dict.copy() or {}
                shallow_context = deepcopy(context_node)
                shallow_xml.append(shallow_context)
                for name, selector in self._variables:
                    selected_value = selector.select(root=shallow_xml, item=shallow_context, variables=evaluated_variables)
                    evaluated_variables.update({name: selected_value})
                shallow_xml.clear()

            # Append copy of InvoiceLine element on the shallow XML
            if self.root_name == "CEN" and context_node.tag == INVOICE_LINE_TAG:
                shallow_line = deepcopy(context_node)
                shallow_xml.append(shallow_line)

            # Run every assertion to the context node
            for assert_id, flag, selector, message in self._assertions:
                if self.root_name == "CEN":
                    if assert_id in ("BR-CO-10", "BR-S-01", "BR-S-08", "BR-S-09"):
                        # These assertions (unfortunately) require us to evaluate the whole XML
                        # because they asks for some value(s) from each InvoiceLine elements.
                        res = selector.select(xml, item=context_node, variables=evaluated_variables)
                    else:
                        res = selector.select(shallow_xml, item=context_node, variables=evaluated_variables)
                else:
                    res = selector.select(context_node, variables=evaluated_variables)

                if not res:
                    # Assert message from CEN schematron already includes the assert code
                    assert_message = message if self.root_name == "CEN" else f"[{assert_id}] {message}"
                    if flag == "warning":
                        warning.append(assert_message)
                    elif flag == "fatal":
                        fatal.append(assert_message)

            # Remove the appended InvoiceLine copy from earlier
            if self.root_name == "CEN" and context_node.tag == INVOICE_LINE_TAG:
                shallow_xml.remove(shallow_xml.getchildren()[-1])

        return warning, fatal

    def add_assert(self, assert_id: str, flag: str, test: str, message: str):
        test_selector = elementpath.Selector(test, namespaces=self.namespaces, parser=parser)
        self._assertions.append((assert_id, flag, test_selector, message))


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
        print(f"timed {name}: {total_time} (rcr={rcr})")
        return True

    return False


def run_schematron(name: str):
    if name not in TEST_MAP:
        raise Exception("Invalid schematron argument!")

    schematron_paths = TEST_MAP[name]["schematron_paths"]
    test_file_path = TEST_MAP[name]["test_file_path"]

    for schematron_path in schematron_paths:
        root_name = PATH_ROOT_MAP[schematron_path]
        print(f"Running {root_name} schematron")
        schematron = ElementSchematron.from_sch(etree.parse(schematron_path).getroot(), root_name)
        doc = etree.parse(test_file_path).getroot()
        warning, fatal = schematron.run(doc)
        if warning:
            print("Warning:")
            pprint(warning)
        if fatal:
            print("Fatal:")
            pprint(fatal)


def main():
    to_run = sys.argv[1]
    print("Running", to_run.upper())
    tta = time()
    run_schematron(to_run)
    pprint(time() - tta)
    print(f"total rcr: {rcr}")
    print(f"total rce: {rce}")


if __name__ == "__main__":
    main()
