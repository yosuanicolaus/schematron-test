import re
import sys
from decimal import Decimal
from time import time
from typing import Generic, List, Optional, Tuple, TypeVar

import elementpath
import ipdb
from lxml import etree
from lxml.etree import _Element
from rich.pretty import pprint
from saxonche import PySaxonProcessor

from myconst import (
    ASSERT_REPLACE_MAP,
    PATH_ROOT_MAP,
    QUERY_REPLACE_MAP,
    TEST_MAP,
    VARIABLE_REPLACE_MAP,
    VARIABLE_TO_IGNORE,
)

parser = elementpath.XPath2Parser
parser.DEFAULT_NAMESPACES.update({"u": "utils"})
method = parser.method
function = parser.function
T = TypeVar("T", bound="Element")

times: dict[str, float] = {
    "evar_old": 0.0,
    "evar_meta": 0.0,
    "ctxn_old": 0.0,
    "ctxn_meta": 0.0,
    "var_old": 0.0,
    "var_meta": 0.0,
    "assert_old": 0.0,
    "assert_meta": 0.0,
}
told = 0
to_save_ids = []

to_handle_map: dict[str, str] = {}
dummy_xml = etree.Element("unused")

gid = ""
gxml = dummy_xml
gnsmap = {}
gvars = {}


# Helper Methods


def cdbg(path: str, **kwargs):
    # Just for debugging, remove when done
    return gxml.xpath(path, namespaces=gnsmap, **gvars, **kwargs)


def _xpath_clean_value(value):
    if not value:
        return ""
    if isinstance(value, list):
        value = value[0]
    if isinstance(value, _Element):
        value = value.text or ""
    return str(value)


def _clean_xpath_query(path: str) -> str:
    """
    Strip and replace all multiple space with a single space
    """
    clean_path_list = []
    for i in range(len(path)):
        if i + 1 < len(path) and path[i] == path[i + 1] == " ":
            continue
        clean_path_list.append(path[i])
    return "".join(clean_path_list).strip()


# LXML XPath Methods


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


def xpath_u_checkSEOrgnr(_, number: str):
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


def xpath_u_for_every(ctx, item_list_path: str, condition_var: str):
    item_list = ctx.context_node.xpath(item_list_path, namespaces=gnsmap, **gvars)

    for item in item_list:
        if isinstance(item, etree._Element):
            item = f"'{item.text}'"
        test = re.sub(r"\$VAR", item, condition_var)
        if not ctx.context_node.xpath(test, namespaces=gnsmap, **gvars):
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
    if not value:
        return 0
    value = float(_xpath_clean_value(value))
    return round(value, int(precision))


def xpath_u_upper_case(_, value):
    value = _xpath_clean_value(value)
    return str(value).upper()


def xpath_u_abs(_, value):
    if not value:
        return 0
    strvalue = _xpath_clean_value(value)
    try:
        value = int(strvalue)
    except ValueError:
        value = float(strvalue)
    return abs(value)


def xpath_u_tokenize_and_index(_, text, delimiter, index):
    if not text:
        return ""
    try:
        tokens = text.split(delimiter)
        return tokens[int(index) - 1] if 0 < int(index) <= len(tokens) else ""  # Handle out-of-bounds
    except (ValueError, IndexError):
        return ""  # Handle invalid index or split errors


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
utils_ns["checkSEOrgnr"] = xpath_u_checkSEOrgnr

# custom utils
utils_ns["for_every"] = xpath_u_for_every
utils_ns["if_else"] = xpath_u_if_else
utils_ns["call_elementpath"] = xpath_u_call_elementpath
utils_ns["exists"] = xpath_u_exists
utils_ns["round"] = xpath_u_round
utils_ns["upper_case"] = xpath_u_upper_case
utils_ns["abs"] = xpath_u_abs
utils_ns["tokenize_and_index"] = xpath_u_tokenize_and_index


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


@method(function("checkSEOrgnr", prefix="u", nargs=1))
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
        self._variables.append((name, elementpath.Selector(_clean_xpath_query(path), namespaces=self.namespaces, parser=parser)))

    @property
    def variables(self):
        if self.parent:
            return self.parent.variables + self._variables
        else:
            return self._variables

    def run(self, xml: _Element, evars_dict: Optional[dict] = None, ovars_dict=None) -> Tuple[List[str], List[str]]:
        """Evaluate the variables at the current level, and then run the children."""
        global times, gxml, gvars, gnsmap, gid
        ovars = ovars_dict and ovars_dict.copy() or {}
        evars = evars_dict and evars_dict.copy() or {}
        gvars = evars
        gnsmap = self.namespaces
        gxml = xml

        for name, selector in self._variables:
            gid = name
            tt = time()
            ovar_val = selector.select(xml, variables=ovars)
            if isinstance(ovar_val, list) and len(ovar_val) == 1:
                ovar_val = ovar_val[0]
            # ovars.update({name: ovar_val})
            ovars[name] = ovar_val
            times["evar_old"] += time() - tt

            if name in VARIABLE_TO_IGNORE:
                continue
            elif name in VARIABLE_REPLACE_MAP:
                path_str = VARIABLE_REPLACE_MAP[name]
            else:
                path_str = selector.path
            try:
                tt = time()
                var_val = xml.xpath(path_str, namespaces=self.namespaces, **evars)
                if isinstance(var_val, list) and len(var_val) == 1:
                    var_val = var_val[0]
                evars[name] = var_val
                times["evar_meta"] += time() - tt
                if var_val != ovar_val:
                    raise Exception("wrong variable value!!")
            except Exception as e:
                print(f"evars get {name} var failed!:", e)
                print(path_str)
                to_handle_map[name] = path_str
                ipdb.set_trace()

        warning, fatal = [], []
        for child in self.children:
            res_warning, res_fatal = child.run(xml, evars_dict=evars, ovars_dict=ovars)
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
        context = _clean_xpath_query(context)

        self.context_path = QUERY_REPLACE_MAP.get(context, context)
        # remove when done
        if self.context_path == "":
            self.context_path = context
        self.context_selector = elementpath.Selector(_clean_xpath_query(context), namespaces=self.namespaces, parser=parser)

        # List of 4 element tuples, consisting of assert_id, flag, test (selector), message
        self._assertions: List[Tuple[str, str, elementpath.Selector, str]] = []
        self.namespaces.update({"re": "http://exslt.org/regular-expressions"})

    def add_assert(self, assert_id: str, flag: str, test: str, message: str):
        # Before appending, "clean" the test first
        test = _clean_xpath_query(test)
        test_selector = elementpath.Selector(test, namespaces=self.namespaces, parser=parser)
        self._assertions.append((assert_id, flag, test_selector, message))

    def run(self, xml: _Element, evars_dict: Optional[dict] = None, ovars_dict: Optional[dict] = None):
        """
        This method overrides Element.run function because ElementRule is at the bottom of the Element tree,
        and it does not have any children.

        Here, we evaluate through all the gathered assertions and variables, and evaluate the XML with some
        strategies to combat the severe performance issues from running elementpath.Selector.select multiple times.
        """
        global times, gnsmap, gvars, gid, gxml
        gnsmap = self.namespaces
        ovars_dict = ovars_dict and ovars_dict.copy() or {}
        evars_dict = evars_dict and evars_dict.copy() or {}
        tt = time()
        context_nodes = self.context_selector.select(xml, variables=ovars_dict)
        times["ctxn_old"] += time() - tt

        try:
            tt = time()
            meta_nodes = xml.xpath(self.context_path, namespaces=self.namespaces, **evars_dict)
            times["ctxn_meta"] += time() - tt
            if meta_nodes != context_nodes:
                raise Exception("success but wrong result!")
        except Exception as e:
            print("meta nodes failed!", e)
            # print(self.context_selector.path)
            print(self.context_path)
            to_handle_map[self.context_path] = ""
            ipdb.set_trace()

        warning, fatal = [], []

        for context_node in context_nodes:
            # If the rule has additional variable, we evaluate them here.
            ovars = ovars_dict.copy()
            evars = evars_dict.copy()

            if self._variables:
                for name, selector in self._variables:
                    if name in VARIABLE_REPLACE_MAP:
                        evar_path = VARIABLE_REPLACE_MAP[name]
                    elif selector.path in QUERY_REPLACE_MAP:
                        evar_path = QUERY_REPLACE_MAP[selector.path]
                    else:
                        evar_path = selector.path

                    tt = time()
                    ovar_val = selector.select(xml, item=context_node, variables=ovars)
                    times["var_old"] += time() - tt
                    ovars[name] = ovar_val

                    try:
                        tt = time()
                        evar_val = context_node.xpath(evar_path, namespaces=self.namespaces, **evars)
                        times["var_meta"] += time() - tt
                        if isinstance(evar_val, list) and len(evar_val) == 1:
                            evar_val = evar_val[0]
                        evars[name] = evar_val
                        if evar_val != ovar_val:
                            if isinstance(ovar_val, Decimal) and float(ovar_val) == evar_val:
                                continue
                            raise Exception("wrong result for rule variable")
                    except Exception as e:
                        print(f"getting assert {name} var failed", e)
                        print(evar_path)
                        to_handle_map[name] = selector.path
                        ipdb.set_trace()

            # evars = ovars.copy()  # TODO: evars independence... achieved?
            # for k, v in evars.items():
            #     if isinstance(v, list) and not isinstance(v[0], _Element):
            #         # xpath variables only accepts strings. For list variables, use space-separated values
            #         evars[k] = " ".join(v)

            gxml = context_node
            gvars = evars

            for assert_id, flag, selector, message in self._assertions:
                gid = assert_id
                tt = time()
                expected = selector.select(xml, item=context_node, variables=ovars)
                times["assert_old"] += time() - tt

                if assert_id in ASSERT_REPLACE_MAP:
                    test_str = ASSERT_REPLACE_MAP[assert_id]
                else:
                    test_str = selector.path

                    if "matches" in test_str:
                        test_str = re.sub(r"matches", "re:match", test_str)

                    if "exists" in test_str:
                        test_str = re.sub(r"exists", "u:exists", test_str)

                    if "xs:decimal" in test_str:
                        test_str = re.sub(r"xs:decimal", "number", test_str)

                try:
                    tt = time()
                    cres = context_node.xpath(test_str, namespaces=self.namespaces, **evars)
                    times["assert_meta"] += time() - tt
                    if cres == expected:
                        pass
                    else:
                        res = xml.xpath(test_str, namespaces=self.namespaces, **evars)
                        if res == expected:
                            print("!!!")
                            print("!!! xpath succeeded only by using root node", assert_id)
                            print("!!!")
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
                    # to_handle_map[assert_id] = ""

        return warning, fatal


def run_schematron(name: str):
    global times
    if name not in TEST_MAP:
        raise Exception("Invalid schematron argument!")

    schematron_paths = TEST_MAP[name]["schematron_paths"]
    test_file_path = TEST_MAP[name]["test_file_path"]

    for schematron_path in schematron_paths:
        root_name = PATH_ROOT_MAP[schematron_path]
        print(f"Running {root_name} schematron on {test_file_path}")
        schematron = ElementSchematron.from_sch(etree.parse(schematron_path).getroot(), root_name)
        doc = etree.parse(test_file_path).getroot()
        warning, fatal = schematron.run(doc)
        print("Times:")
        pprint(times, expand_all=True)
        print("Warning:")
        pprint(warning)
        print("Fatal:")
        pprint(fatal)
        print(
            sum(times.values()),
            sum(v for k, v in times.items() if "_old" in k),
            sum(v for k, v in times.items() if "_meta" in k),
        )
        times = {k: 0.0 for k in times}  # reset times for the next schematron


def main():
    to_run = sys.argv[1]
    if to_run == "saxonche":
        saxonche()
        return

    tt = time()
    run_schematron(to_run)
    pprint(time() - tt)


def saxonche():
    tt = time()
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        peppol_sch = xsltproc.compile_stylesheet(stylesheet_file="./validation/saxonche/peppol.xsl")
        cen_sch = xsltproc.compile_stylesheet(stylesheet_file="./validation/saxonche/cen.xsl")

    with PySaxonProcessor(license=False):
        for sch in (cen_sch, peppol_sch):
            print(f"Running {'CEN' if sch == cen_sch else 'PEPPOL'}")
            output = sch.transform_to_string(source_file=TEST_MAP["peppol100"]["test_file_path"])
            svrl = etree.fromstring(output.encode()).getroottree()
            warning = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="warning"]')]
            fatal = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="fatal"]')]
            print("Warning:")
            pprint(warning)
            print("Fatal:")
            pprint(fatal)

    print(time() - tt)


if __name__ == "__main__":
    main()

if 2 == 1:
    # To keep the import from deleted by autocomplete
    ipdb.set_trace()

print(to_handle_map)
print(len(to_handle_map))
