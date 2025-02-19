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

from myconst import (
    ASSERT_REPLACE_MAP,
    GNSMAP,
    PATH_ROOT_MAP,
    QUERY_REPLACE_MAP,
    TEST_MAP,
    VARIABLE_REPLACE_MAP,
    VARIABLE_TO_IGNORE,
)

XPathList = list[_Element]
XPathObject = bool | str | float | XPathList
T = TypeVar("T", bound="Element")

to_handle_map: dict[str, str] = {}
dummy_xml = etree.Element("unused")

utils_ns = etree.FunctionNamespace("utils")
utils_ns.prefix = "u"


# Sync everything below until just before Script Logic with `schematron_validation.py`

################################################################################
# Helper Methods
################################################################################


def try_xpath(xml: _Element, path: str, namespaces: dict, variables: dict) -> XPathObject:
    try:
        val = xml.xpath(path, namespaces=namespaces, **variables)
        # TODO (if needed): convert _XPathObject (lxml) to XPathObject (custom); handle other possible lxml _XPathObject types
        return val
    except Exception as e:
        # TODO: Log error here
        print(f"XPath failed ({e}) on path:\n%s" % path)
        return False


def _xpath_clean_value(xpath_object: XPathObject) -> str:
    val = ""
    if not xpath_object:
        return val

    if isinstance(xpath_object, list):
        val = xpath_object[0]
        if isinstance(val, _Element):
            return val.text or ""
        else:
            return str(val)
    else:
        val = xpath_object

    return str(val)


def _xpath_normalize_query(path: str) -> str:
    """
    Strip and replace all multiple spaces with a single space
    """
    clean_path_list = []
    for i in range(len(path)):
        if i + 1 < len(path) and path[i] == path[i + 1] == " ":
            continue
        clean_path_list.append(path[i])
    return "".join(clean_path_list).strip()


def _xpath_transform_query(query: str) -> str:
    """
    Transform simple XPath 2.0 syntax with custom function
    """
    if "matches" in query:
        query = re.sub(r"matches", "re:match", query)
    if "exists" in query:
        query = re.sub(r"exists", "u:exists", query)
    if "xs:decimal" in query:
        query = re.sub(r"xs:decimal", "number", query)
    if "upper-case" in query:
        query = re.sub(r"upper-case", "u:upper_case", query)
    if "xs:integer" in query:
        query = re.sub(r"xs:integer", "number", query)
    if "tokenize" in query:
        query = re.sub(r"tokenize", "u:tokenize", query)
    if "string-join" in query:
        query = re.sub(r"string-join", "u:string_join", query)

    return query


def _make_xpath_list(list_var: list[str]) -> XPathList:
    """
    Create a list of lxml.etree._Element object so that it can be passed
    by lxml in custom functions, and be destructured into a normal `list[str]` variable.
    All the string values will be stored inside the _Element object's `text`.
    """
    elements = []
    for var in list_var:
        element = etree.Element("t")
        element.text = var
        elements.append(element)
    return elements


def _destructure_xpath_list(xpath_list_var: XPathList) -> list[str]:
    return [(t.text or "") for t in xpath_list_var]


################################################################################
# LXML XPath Utility Methods from the Schematrons
################################################################################


@utils_ns("gln")
def xpath_u_gln(_, val: str):
    weighted_sum = sum(num * (1 + (((index + 1) % 2) * 2)) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return (10 - (weighted_sum % 10)) % 10 == int(val[-1])


@utils_ns("slack")
def xpath_u_slack(_, exp: float, val: float, slack: float):
    return (exp + slack) >= val and (exp - slack) <= val


@utils_ns("mod11")
def xpath_u_mod11(_, val: str):
    weighted_sum = sum(num * ((index % 6) + 2) for index, num in enumerate([ord(c) - 48 for c in val[:-1]][::-1]))
    return int(val) > 0 and (11 - (weighted_sum % 11)) % 11 == int(val[-1])


@utils_ns("mod97-0208")
def xpath_u_mod97_0208(_, val: str):
    val = val[2:]
    return int(val[-2:]) == 97 - (int(val[:-2]) % 97)


@utils_ns("checkCodiceIPA")
def xpath_u_checkCodiceIPA(_, val: str):
    return bool(len(val) == 6 and re.match("^[a-zA-Z0-9]+$", val))


@utils_ns("checkCF16")
def xpath_u_checkCF16(_, val: str):
    return bool(re.fullmatch(r"[a-zA-Z]{6}\d{2}[a-zA-Z]\d{2}[a-zA-Z\d]{3}\d[a-zA-Z]", val))


@utils_ns("checkCF")
def xpath_u_checkCF(_, val: str):
    if len(val) == 16:
        return xpath_u_checkCF16(_, val)
    elif len(val) == 11:
        return val.isnumeric()
    return False


def _xpath_u_addPIVA(arg: str, pari: bool):
    # Because of the way the xpath substr function works, the base case is arg as an empty string
    # pari is used to alterate, such that the CHECK_NO ("0246813579") is indexed every other character
    if not arg.isnumeric():
        return 0
    else:
        if pari:
            return int("0246813579"[int(arg[0])]) + _xpath_u_addPIVA(arg[1:], not pari)
        else:
            return int(arg[0]) + _xpath_u_addPIVA(arg[1:], not pari)


@utils_ns("checkPIVA")
def xpath_u_checkPIVA(_, val: str):
    if not val.isnumeric():
        return 1
    return _xpath_u_addPIVA(val, False) % 10


@utils_ns("addPIVA")
def xpath_u_addPIVA(_, arg: str, pari: int):
    return _xpath_u_addPIVA(arg, bool(pari))


@utils_ns("checkPIVAseIT")
def xpath_u_checkPIVAseIT(_, val: str):
    if val[:2].upper() != "IT" or len(val) != 13:
        return False
    else:
        return bool(_xpath_u_addPIVA(val[2:], False) % 10 == 0)


@utils_ns("abn")
def xpath_u_abn(_, val: str):
    subtractors = [49] + [48] * 10
    multipliers = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    return bool(sum((ord(character) - subtractors[index]) * multipliers[index] for index, character in enumerate(val)) % 89 == 0)


@utils_ns("TinVerification")
def xpath_u_TinVerification(_, val: XPathObject):
    val = _xpath_clean_value(val)
    val = "".join([ch for ch in val if ch.isnumeric()])
    return sum(int(character) * (2 ** (index + 1)) for index, character in enumerate(val[:8][::-1])) % 11 % 10 == int(val[-1])


@utils_ns("checkSEOrgnr")
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


################################################################################
# LXML XPath Custom Utility Methods
################################################################################


@utils_ns("for_every")
def xpath_u_for_every(ctx, item_list: XPathList, condition_var: str):
    for item in item_list:
        res = ctx.context_node.xpath(condition_var, namespaces=GNSMAP, VAR=item)
        if not res:
            return False

    return True


@utils_ns("id_SCH_EUSR_40")
def xpath_u_id_SCH_EUSR_40(ctx):
    """
    Handles Assert SCH-EUSR-40:
    every $st in (eusr:Subset[normalize-space(@type) = 'PerEUC']), $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry'])
    satisfies count(
        eusr:Subset[normalize-space(@type) ='PerEUC'][
            every $euc in (eusr:Key[normalize-space(@schemeID) = 'EndUserCountry'])
            satisfies normalize-space($euc) = normalize-space($steuc)
        ]) = 1
    """
    subset_nodes = ctx.context_node.xpath("eusr:Subset[normalize-space(@type) = 'PerEUC']", namespaces=GNSMAP)

    if not subset_nodes:
        return True

    for subset_node in subset_nodes:
        key_nodes = subset_node.xpath("eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']", namespaces=GNSMAP)
        if not key_nodes:
            continue

        for key_node in key_nodes:
            key_value = key_node.text
            count = 0
            other_subset_nodes = ctx.context_node.xpath("eusr:Subset[normalize-space(@type) = 'PerEUC']", namespaces=GNSMAP)
            for other_subset_node in other_subset_nodes:
                other_key_nodes = other_subset_node.xpath("eusr:Key[normalize-space(@schemeID) = 'EndUserCountry']", namespaces=GNSMAP)
                for other_key_node in other_key_nodes:
                    if other_key_node.text == key_value:
                        count += 1
            if count != 1:
                return False

    return True


@utils_ns("if_else")
def xpath_u_if_else(_, condition, then_clause, else_clause):
    if condition:
        return then_clause
    else:
        return else_clause


@utils_ns("castable")
def xpath_u_castable(_, value: str, cast_type: str):
    return elementpath.select(dummy_xml, f"'{value}' castable as xs:{cast_type}")


@utils_ns("exists")
def xpath_u_exists(_, value):
    return bool(value)


@utils_ns("round")
def xpath_u_round(_, value: float, precision: float):
    if not value:
        return 0
    return round(value, int(precision))


@utils_ns("upper_case")
def xpath_u_upper_case(_, value):
    value = _xpath_clean_value(value)
    return str(value).upper()


@utils_ns("abs")
def xpath_u_abs(_, value):
    if not value:
        return 0
    strvalue = _xpath_clean_value(value)
    try:
        value = int(strvalue)
    except ValueError:
        value = float(strvalue)
    return abs(value)


@utils_ns("int")
def xpath_u_int(_, value):
    return int(value)


@utils_ns("max")
def xpath_u_max(_, value):
    num_values = []
    if isinstance(value, list):
        for node in value:
            num_values.append(float(node.text))
    elif isinstance(value, int | float):
        return value
    return max(num_values) if num_values else 0


@utils_ns("tokenize_and_index")
def xpath_u_tokenize_and_index(_, text, delimiter, index):
    if not text:
        return ""
    try:
        tokens = text.split(delimiter)
        return tokens[int(index) - 1] if 0 < int(index) <= len(tokens) else ""  # Handle out-of-bounds
    except (ValueError, IndexError):
        return ""  # Handle invalid index or split errors


@utils_ns("compare_date")
def xpath_u_compare_date(_, date1, operator: str, date2):
    """
    param str operator: Either '<', '>', '<=', or '>='. If not any of them, this method will return False.
    """
    date1 = _xpath_clean_value(date1)
    date2 = _xpath_clean_value(date2)
    match operator:
        case "<":
            return date1 < date2
        case "<=":
            return date1 <= date2
        case ">":
            return date1 > date2
        case ">=":
            return date1 >= date2
        case _:
            return False


@utils_ns("tokenize")
def xpath_u_tokenize(_, value, delimiter: str):
    str_value = _xpath_clean_value(value)
    if not str_value:
        return []
    return _make_xpath_list(str_value.split(delimiter))


@utils_ns("string_join")
def xpath_u_string_join(_, elements: XPathList, joiner: str):
    return joiner.join(_destructure_xpath_list(elements))


################################################################################
# Main Logic
################################################################################


class Element(Generic[T]):
    def __init__(self, namespaces: dict[str, str], parent: Optional["Element"] = None):
        self.namespaces = namespaces
        self.children: List[T] = []
        self._variables: List[Tuple[str, str]] = []
        self.parent: Optional[Element] = parent
        self.root_name: Optional[str] = parent and parent.root_name

    def add_variable(self, name: str, path: str):
        query = _xpath_normalize_query(path)
        query = VARIABLE_REPLACE_MAP.get(name, QUERY_REPLACE_MAP.get(query, _xpath_transform_query(query)))
        self._variables.append((name, query))

    @property
    def variables(self):
        if self.parent:
            return self.parent.variables + self._variables
        else:
            return self._variables

    def run(self, xml: _Element, variables_dict: Optional[dict] = None) -> Tuple[List[str], List[str]]:
        """Evaluate the variables at the current level, and then run the children."""
        evars = variables_dict and variables_dict.copy() or {}

        for name, query in self._variables:
            if name in VARIABLE_TO_IGNORE:
                continue

            evars[name] = try_xpath(xml, query, self.namespaces, evars)

        warning, fatal = [], []
        for child in self.children:
            res_warning, res_fatal = child.run(xml, variables_dict=evars)
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
                element.add_variable(var.get("name") or "", var.get("value") or "")

        # This is the namespace used to interpret the sch file
        sch_namespace = {"": "http://purl.oclc.org/dsdl/schematron"}

        # Generate the namespaces used to interpet the documents to be validated
        namespace_dict: dict[str, str] = {"re": "http://exslt.org/regular-expressions"}
        for ns in sch.findall("./ns", namespaces=sch_namespace):
            namespace_dict.update({ns.get("prefix") or "": ns.get("uri") or ""})

        schematron = cls(namespaces=namespace_dict, parent=None)
        schematron.root_name = root_name
        add_all_variable(schematron, sch)

        for pattern_node in sch.findall("./pattern", namespaces=sch_namespace):
            pattern = schematron.add_element_pattern(pattern_node.get("id") or "")
            add_all_variable(pattern, pattern_node)

            for rule_node in pattern_node.findall("./rule", namespaces=sch_namespace):
                rule = pattern.add_element_rule(rule_node.get("context") or "")
                add_all_variable(rule, rule_node)
                for assertion in rule_node.findall("./assert", namespaces=sch_namespace):
                    rule.add_assert(
                        assertion.get("id") or "",
                        assertion.get("flag") or "",
                        assertion.get("test") or "",
                        assertion.text or "",
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
        context = _xpath_normalize_query(context)
        self.context_path = QUERY_REPLACE_MAP.get(context, _xpath_transform_query(context))

        # List of 4 element tuples, consisting of assert_id, flag, query, message
        self._assertions: List[Tuple[str, str, str, str]] = []
        # self.namespaces.update({"re": "http://exslt.org/regular-expressions"})

    def add_assert(self, assert_id: str, flag: str, test: str, message: str):
        query = _xpath_normalize_query(test)
        query = ASSERT_REPLACE_MAP.get(assert_id, _xpath_transform_query(query))
        self._assertions.append((assert_id, flag, query, message))

    def run(self, xml: _Element, variables_dict: Optional[dict] = None):
        """
        This method overrides Element.run function because ElementRule is at the bottom of the Element tree,
        and it does not have any children.

        Here, we evaluate through all the gathered assertions and variables, and evaluate the XML with some
        strategies to combat the severe performance issues from running elementpath.Selector.select multiple times.
        """
        variables_dict = variables_dict and variables_dict.copy() or {}
        context_nodes = try_xpath(xml, self.context_path, self.namespaces, variables_dict)
        warning, fatal = [], []

        if not isinstance(context_nodes, list):
            return warning, fatal

        for context_node in context_nodes:
            if not isinstance(context_node, _Element):
                continue

            # If the rule has additional variable, we evaluate them here.
            evars: dict[str, XPathObject] = variables_dict.copy()

            if self._variables:
                for name, query in self._variables:
                    evars[name] = try_xpath(context_node, query, self.namespaces, evars)

            for assert_id, flag, query, message in self._assertions:
                res = try_xpath(context_node, query, self.namespaces, evars)
                if not res:
                    assert_message = f"[{assert_id}]-{message}" if self.root_name == "PEPPOL" else message
                    if flag == "warning":
                        warning.append(assert_message)
                    elif flag == "fatal":
                        fatal.append(assert_message)

        return warning, fatal


################################################################################
# Script Logic (not to copy to odoo)
################################################################################


def run_schematron(name: str):
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
        print("Warning:")
        pprint(warning)
        print("Fatal:")
        pprint(fatal)


def main():
    to_run = sys.argv[1]
    if to_run == "saxonche":
        saxonche()
        return

    if len(sys.argv) > 2:
        global stress_mode
        stress_mode = sys.argv[2].upper()

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
