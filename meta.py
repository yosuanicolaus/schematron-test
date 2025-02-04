import re
import sys
from time import time
from typing import Generic, List, Optional, Tuple, TypeVar

import elementpath
import ipdb
from lxml import etree
from lxml.etree import _Element
from rich.pretty import pprint
from saxonche import PySaxonProcessor

from myconst import PATH_ROOT_MAP, TEST_MAP, TEST_REPLACE_MAP

parser = elementpath.XPath2Parser
parser.DEFAULT_NAMESPACES.update({"u": "utils"})
method = parser.method
function = parser.function
T = TypeVar("T", bound="Element")

tvmeta = 0.0
tvhack = 0.0
tameta = 0.0
tahack = 0.0
told = 0
to_save_ids = []

to_handle_map: dict[str, str] = {}
dummy_xml = etree.Element("unused")

gnsmap = {}
gvars = {}


def xpath_u_gln(_, val):
    weighted_sum = sum(num * (1 + (((index + 1) % 2) * 2)) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return (10 - (weighted_sum % 10)) % 10 == int(val[-1])


def xpath_u_slack(_, exp, val, slack):
    return (exp + slack) >= val and (exp - slack) <= val


def xpath_u_mod11(_, val):
    weighted_sum = sum(num * ((index % 6) + 2) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return int(val) > 0 and (11 - (weighted_sum % 11)) % 11 == int(val[-1])


def xpath_u_mod97_0208(_, val):
    val = val[2:]
    return int(val[-2:]) == 97 - (int(val[:-2]) % 97)


def xpath_u_checkCodiceIPA(_, val):
    return bool(len(val) == 6 and re.match("^[a-zA-Z0-9]+$", val))


def xpath_u_checkCF16(_, val):
    return bool(re.fullmatch(r"[a-zA-Z]{6}\d{2}[a-zA-Z]\d{2}[a-zA-Z\d]{3}\d[a-zA-Z]", val))


def xpath_u_checkCF(_, val):
    if len(val) == 16:
        return xpath_u_checkCF16(_, val)
    elif len(val) == 11:
        return val.isnumeric()
    return False


def _xpath_u_addPIVA(arg, pari):
    # Because of the way the xpath substr function works, the base case is arg as an empty string
    # pari is used to alterate, such that the CHECK_NO ("0246813579") is indexed every other character
    if not arg.isnumeric():
        return 0
    else:
        if pari:
            return int("0246813579"[int(arg[0])]) + _xpath_u_addPIVA(arg[1:], not pari)
        else:
            return int(arg[0]) + _xpath_u_addPIVA(arg[1:], not pari)


def xpath_u_checkPIVA(_, val):
    if not val.isnumeric:
        return 1
    return _xpath_u_addPIVA(val, False) % 10


def xpath_u_addPIVA(_, arg, pari):
    return _xpath_u_addPIVA(arg, pari)


def xpath_u_checkPIVAseIT(_, val):
    if val[:2].upper() != "IT" or len(val) != 13:
        return False
    else:
        return bool(_xpath_u_addPIVA(val[2:], False) % 10 == 0)


def xpath_u_abn(_, val: str):
    subtractors = [49] + [48] * 10
    multipliers = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return bool(sum((ord(character) - subtractors[index]) * multipliers[index] for index, character in enumerate(val)) % 89 == 0)


def xpath_u_TinVerification(_, val: str):
    return sum(int(character) * (2 ** (index + 1)) for index, character in enumerate(val[:8][::-1])) % 11 % 10 == int(val[-1])


def xpath_u_for_some(ctx, item_list_str: str, condition_var: str):
    item_list = item_list_str.split(" ")

    for item in item_list:
        test = re.sub(r"\$VAR", item, condition_var)
        if ctx.context_node.xpath(test):
            ipdb.set_trace()
            return True

    return False


def xpath_u_for_every(ctx, item_list_path: str, condition_var: str):
    global gnsmap, gvars
    item_list = ctx.context_node.xpath(item_list_path, namespaces=gnsmap, **gvars)

    for item in item_list:
        test = re.sub(r"\$VAR", item, condition_var)
        if not ctx.context_node.xpath(test, namespaces=gnsmap, **gvars):
            ipdb.set_trace()
            return False

    return True


def xpath_u_if_else(_, condition, then_clause, else_clause):
    if condition:
        return then_clause
    else:
        return else_clause


def xpath_u_call_elementpath(_, template: str, value: str):
    return elementpath.select(dummy_xml, template % value)


def xpath_u_exists(_, value):
    return bool(value)


def xpath_u_round(_, value, precision):
    # ipdb.set_trace()
    return round(value, int(precision))


utils_ns = etree.FunctionNamespace("utils")
utils_ns.prefix = "u"

# util functions from the peppol schematron
utils_ns["gln"] = xpath_u_gln
utils_ns["slack"] = xpath_u_slack
utils_ns["mod11"] = xpath_u_mod11
utils_ns["mod97-0208"] = xpath_u_mod97_0208
utils_ns["checkCodiceIPA"] = xpath_u_checkCodiceIPA
utils_ns["checkCF"] = xpath_u_checkCF
utils_ns["checkCF16"] = xpath_u_checkCF16
utils_ns["checkPIVA"] = xpath_u_checkPIVA
utils_ns["addPIVA"] = xpath_u_addPIVA
utils_ns["checkPIVAseIT"] = xpath_u_checkPIVAseIT
utils_ns["abn"] = xpath_u_abn
utils_ns["TinVerification"] = xpath_u_TinVerification

# custom utils
utils_ns["for_some"] = xpath_u_for_some
utils_ns["for_every"] = xpath_u_for_every
utils_ns["if_else"] = xpath_u_if_else
utils_ns["call_elementpath"] = xpath_u_call_elementpath
utils_ns["exists"] = xpath_u_exists
utils_ns["round"] = xpath_u_round


def make_if_statement(condition: str, true_statement: str, false_statement: str) -> str:
    return f"""if ({condition}):
    {true_statement}
else:
    {false_statement}"""


################################################################################
# Parser Functions
################################################################################


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
        self.namespaces.update({"re": "http://exslt.org/regular-expressions"})

    def add_assert(self, assert_id: str, flag: str, test: str, message: str):
        # Before appending, "clean" the test first
        if "satisfies" in test:
            pass
            # print(test)
            # ipdb.set_trace()

        clean_test = []
        for i in range(len(test)):
            if i + 1 < len(test) and test[i] == test[i + 1] == " ":
                continue
            clean_test.append(test[i])

        test = "".join(clean_test).strip()
        test_selector = elementpath.Selector(test, namespaces=self.namespaces, parser=parser)
        self._assertions.append((assert_id, flag, test_selector, message))

    def run(self, xml: _Element, variables_dict: Optional[dict] = None):
        """
        This method overrides Element.run function because ElementRule is at the bottom of the Element tree,
        and it does not have any children.

        Here, we evaluate through all the gathered assertions and variables, and evaluate the XML with some
        strategies to combat the severe performance issues from running elementpath.Selector.select multiple times.
        """
        global tameta, tahack, tvmeta, tvhack, gnsmap, gvars
        gnsmap = self.namespaces
        evars = variables_dict and variables_dict.copy() or {}
        context_nodes = self.context_selector.select(xml, variables=variables_dict)
        warning, fatal = [], []

        for context_node in context_nodes:
            # If the rule has additional variable, we evaluate them here.
            ovars = variables_dict and variables_dict.copy() or {}
            if self._variables:
                for name, selector in self._variables:
                    oselect = selector.select(xml, item=context_node, variables=ovars)
                    ovars.update({name: oselect})

            evars = ovars.copy()
            for k, v in evars.items():
                if isinstance(v, list) and not isinstance(v[0], _Element):
                    # xpath variables only accepts strings. For list variables, use space-separated values
                    evars[k] = " ".join(v)

            gvars = evars

            def cdbg(path):
                return context_node.xpath(path, namespaces=self.namespaces, **evars)

            for assert_id, flag, selector, message in self._assertions:
                th = time()
                expected = selector.select(xml, item=context_node, variables=ovars)
                tahack += time() - th

                test_str = selector.path
                if "matches" in test_str:
                    test_str = re.sub(r"matches", "re:match", test_str)

                if "exists" in test_str:
                    test_str = re.sub(r"exists", "u:exists", test_str)

                if "xs:decimal" in test_str:
                    test_str = re.sub(r"xs:decimal", "number", test_str)

                # if "satisfies" in test_str:
                #     if "some" in test_str:
                #         to_handle_map[test_str] = "contains('{FULL_LIST_CONST}', concat(' ', @varHere, ' '))"

                if test_str in TEST_REPLACE_MAP:
                    test_str = TEST_REPLACE_MAP[test_str]

                try:
                    tm = time()
                    cres = context_node.xpath(test_str, namespaces=self.namespaces, **evars)
                    tameta += time() - tm
                    res = xml.xpath(test_str, namespaces=self.namespaces, **evars)
                    if cres == expected:
                        print("xpath succeeded!", cres)
                    elif res == expected:
                        print("!!!")
                        print("!!! xpath succeeded only by using root node", assert_id)
                        print("!!!")
                    else:
                        raise Exception("xpath succeeded but wrong result!")

                    if not cres:
                        assert_message = message if self.root_name == "CEN" else f"[{assert_id}] {message}"
                        if flag == "warning":
                            warning.append(assert_message)
                        elif flag == "fatal":
                            fatal.append(assert_message)

                except Exception as e:
                    print(assert_id)
                    print(test_str)
                    print("xpath failed!", e)
                    ipdb.set_trace()
                    # to_handle_map[test_str] = test_str

        return warning, fatal


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
        print(f"timed {name}: {total_time}")
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
    if to_run == "saxonche":
        saxonche()
        return

    print("Running", to_run.upper())
    tta = time()
    run_schematron(to_run)
    pprint(time() - tta)
    print(f"total tmeta: {tameta}")
    print(f"total thack: {tahack}")
    # print(to_save_ids)
    print(len(to_save_ids))


def saxonche():
    tt = time()
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        peppol_sch = xsltproc.compile_stylesheet(stylesheet_file="./validation/saxonche/peppol.xsl")

    with PySaxonProcessor(license=False):
        output = peppol_sch.transform_to_string(source_file=TEST_MAP["peppol100"]["test_file_path"])
        svrl = etree.fromstring(output.encode()).getroottree()
        warning = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="warning"]')]
        fatal = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="fatal"]')]

        print("Warning:")
        pprint(warning)
        print("Fatal:")
        pprint(fatal)

    print(time() - tt)

    # CEN_EN16931_UBL, PEPPOL_EN16931_UBL, EUSR, TSR, NLCIUS = (
    #     xsltproc.compile_stylesheet(stylesheet_file=get_module_resource(*SCHEMATRON_PATH, fname))
    #     for fname in (
    #         "CEN-EN16931-UBL.xsl",
    #         "PEPPOL-EN16931-UBL.xsl",
    #         "peppol-end-user-statistics-reporting-1.1.5.xsl",
    #         "peppol-transaction-statistics-reporting-1.0.5.xsl",
    #         "si-ubl-2.0.xsl",
    #     )
    # )


if __name__ == "__main__":
    main()

if 2 == 1:
    # To keep the import from deleted by autocomplete
    ipdb.set_trace()

print(to_handle_map)
