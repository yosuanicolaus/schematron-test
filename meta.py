import re
import sys
from decimal import Decimal
from time import time
from typing import Any, Generic, List, Optional, Tuple, TypeVar

import elementpath
import ipdb
from lxml import etree
from lxml.etree import _Element
from rich.pretty import pprint

from myconst import (
    ASSERT_REPLACE_MAP,
    GNSMAP,
    PATH_ROOT_MAP,
    QUERY_REPLACE_MAP,
    VARIABLE_REPLACE_MAP,
    VARIABLE_TO_IGNORE,
    get_file_and_schematron_paths,
)

parser = elementpath.XPath2Parser
parser.DEFAULT_NAMESPACES.update({"u": "utils"})
method = parser.method
function = parser.function

XPathList = list[_Element]
XPathObject = bool | str | float | XPathList
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
    "stress": 0.0,
}

to_handle_map: dict[str, str] = {}
dummy_xml = etree.Element("unused")

gid = ""
gxml = dummy_xml
gnsmap = {}
gvars = {}
stress_mode = ""

utils_ns = etree.FunctionNamespace("utils")
utils_ns.prefix = "u"


################################################################################
# Debugging Methods
################################################################################


def odbg(path: str, **kwargs):
    # For stress debugging with old approach
    return elementpath.select(gxml, path, namespaces=gnsmap, variables=gvars, **kwargs)


def cdbg(path: str, **kwargs):
    # For quick debugging
    return gxml.xpath(path, namespaces=gnsmap, **gvars, **kwargs)


def try_xpath(
    xml: _Element,
    path: str,
    namespaces: dict,
    vars: dict,
    expected_val: Any,
    times_name: str,
    to_handle_key: str,
    compare: bool = True,
):
    global times, gxml, gnsmap, gvars, gid
    gxml = xml
    gid = to_handle_key
    gnsmap = namespaces
    gvars = vars
    calc_val = False
    try:
        tt = time()
        val = xml.xpath(path, namespaces=namespaces, **vars)
        times[times_name] += time() - tt
        calc_val = val
        if compare and val != expected_val:
            if isinstance(expected_val, list) and len(expected_val) == 1 and expected_val[0] == val:
                pass
            elif (
                isinstance(expected_val, list)
                and len(expected_val) > 0
                and isinstance(expected_val[0], str)
                and isinstance(calc_val, list)
                and len(calc_val) > 0
                and isinstance(calc_val[0], _Element)
                and _destructure_xpath_list(calc_val) == expected_val
            ):
                pass
            elif isinstance(expected_val, Decimal) and isinstance(val, float) and float(expected_val) == val:
                pass
            else:
                raise Exception("xpath succeeded but wrong result")

        if gid == "profile":
            pass
        return val
    except Exception as e:
        print(f"Error when running {times_name}")
        print(f"Exception: {e}")
        print("Key:", to_handle_key)
        print(path)
        if calc_val is not False:
            print("-Expected- Value:", expected_val)
            print("Calculated Value:", calc_val)
        if to_handle_key:
            to_handle_map[to_handle_key] = path
        else:
            to_handle_map[path] = ""
        if str(e) == "Invalid expression":
            pass
        ipdb.set_trace()
        return calc_val


################################################################################
# Helper Methods
################################################################################


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
    Strip and replace all multiple space with a single space
    """
    clean_path_list = []
    for i in range(len(path)):
        if i + 1 < len(path) and path[i] == path[i + 1] == " ":
            continue
        clean_path_list.append(path[i])
    return "".join(clean_path_list).strip()


def _xpath_transform_query(path: str) -> str:
    """
    Replace some simple XPath 2.0 syntax with custom function
    """
    if "matches" in path:
        path = re.sub(r"matches", "re:match", path)
    if "exists" in path:
        path = re.sub(r"exists", "u:exists", path)
    if "xs:decimal" in path:
        path = re.sub(r"xs:decimal", "number", path)
    if "upper-case" in path:
        path = re.sub(r"upper-case", "u:upper_case", path)
    if "xs:integer" in path:
        path = re.sub(r"xs:integer", "number", path)
    if "tokenize" in path:
        path = re.sub(r"tokenize", "u:tokenize", path)
    if "string-join" in path:
        path = re.sub(r"string-join", "u:string_join", path)
    if "cbc:ChargeIndicator = false()" in path:
        path = re.sub(r"cbc:ChargeIndicator = false\(\)", "cbc:ChargeIndicator = 'false'", path)
    if "cbc:ChargeIndicator = true()" in path:
        path = re.sub(r"cbc:ChargeIndicator = true\(\)", "cbc:ChargeIndicator = 'true'", path)

    return path


def _make_xpath_list(list_var: list[str]) -> XPathList:
    """
    Create a list of lxml.etree._Element object so that it can be passed
    by lxml in custom functions, and be destructured into a normal `list[str]` variable.
    All of the string values will be stored inside the _Element object's `text`.
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
# LXML XPath Utility Methods required for the Peppol Schematron
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
    """
    Handles translating the complex ``every ... in ... satisfies ...`` XPath2 query.
    The variable name is dropped and replaced with ``$VAR``, which will be injected with each item of the list.
    For example:
    XPath2: every $varname in $listname satisfies $varname = 42
    XPath1: u:for_every($listname, "$VAR = 42")
    """
    for item in item_list:
        res = ctx.context_node.xpath(condition_var, namespaces=GNSMAP, VAR=item)
        if not res:
            return False

    return True


@utils_ns("if_else")
def xpath_u_if_else(_, condition, then_clause, else_clause):
    """
    Handles translating the complex ``if ... then ... else ...`` XPath2 query.
    For example:
    XPath2: if ($something) then (42) else (24)
    XPath1: u:if($something, 42, 24)
    """
    if condition:
        return then_clause
    else:
        return else_clause


@utils_ns("castable")
def xpath_u_castable(_, value: str, cast_type: str):
    """
    Handles translating the complex ``castable`` type check query in XPath2.
    For example:
    XPath2: $str castable as xs:date
    XPath1: u:castable($str, 'date')
    """
    return elementpath.select(dummy_xml, f"'{value}' castable as xs:{cast_type}")


@utils_ns("exists")
def xpath_u_exists(_, value):
    """Drop in replacement for the XPath2 ``exists`` method"""
    return bool(value)


@utils_ns("round")
def xpath_u_round(_, value: float, precision: float):
    """
    Handles translating the complex round to 2 digit query in XPath2.
    For example:
    XPath2: (round($num * 10 * 10) div 100)
    XPath1: u:round($num, 2)
    """
    if not value:
        return 0
    return round(value, int(precision))


@utils_ns("upper_case")
def xpath_u_upper_case(_, value):
    """Drop in replacement for the XPath2 ``upper-case`` method"""
    value = _xpath_clean_value(value)
    return str(value).upper()


@utils_ns("abs")
def xpath_u_abs(_, value):
    """Drop in replacement for the XPath2 ``max`` method"""
    if not value:
        return 0
    strvalue = _xpath_clean_value(value)
    try:
        value = int(strvalue)
    except ValueError:
        value = float(strvalue)
    return abs(value)


@utils_ns("max")
def xpath_u_max(_, value):
    """Drop in replacement for the XPath2 ``max`` method"""
    num_values = []
    if isinstance(value, list):
        for node in value:
            num_values.append(float(node.text))
    elif isinstance(value, int | float):
        return value
    return max(num_values) if num_values else 0


@utils_ns("compare_date")
def xpath_u_compare_date(_, date1, operator: str, date2):
    """
    Handles translating the date comparison query
    For example:
    XPath2: ``xs:date($date1) < xs:date($date2)``
    XPath1: ``u:compare_date($date1, '<', $date2)``
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
def xpath_u_tokenize(_, value, delimiter: str) -> XPathList:
    """
    Drop-in replacement for the XPath2 `tokenize` method.
    Returns an ``XPathList`` (or ``list[_Element]``) object.
    For example:
    XPath2: tokenize('1 3 5', ' ')
    XPath1: u:tokenize('1 3 5', ' ')
    """
    str_value = _xpath_clean_value(value)
    if not str_value:
        return []
    return _make_xpath_list(str_value.split(delimiter))


@utils_ns("string_join")
def xpath_u_string_join(_, elements: list[str] | list[_Element], joiner: str) -> str:
    """Drop-in replacement for the XPath2 ``sting-join`` method."""
    if not elements:
        return ""
    elif isinstance(elements[0], str):
        # `elements` are list[str]
        return joiner.join(elements)
    else:
        # `elements` are list[_Element]
        return joiner.join(_destructure_xpath_list(elements))


@utils_ns("replace")
def xpath_u_replace(_, value: XPathObject, pattern: str, replacement: str) -> str:
    """Drop-in replacement for the XPath2 ``replace`` method."""
    value = _xpath_clean_value(value)
    return value.replace(pattern, replacement)


################################################################################
# LXML XPath Complex Query Helper Methods
################################################################################


@utils_ns("id_SCH_EUSR_40")
def xpath_u_id_sch_eusr_40(ctx):
    """
    Handles assert ``SCH-EUSR-40``:
        every $st in (eusr:Subset[normalize-space(@type) = 'PerEUC']),
              $steuc in ($st/eusr:Key[normalize-space(@schemeID) = 'EndUserCountry'])
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


@utils_ns("xrechnung_verify_iban")
def xpath_u_xrechnung_verify_iban(_, value: str) -> bool:
    """
    Handles complex XPath2 subquery in assert ``BR-DE-19`` and ``BR-DE-20``:
        number(u:string_join(
            for $cp in
                string-to-codepoints(<concatted-iban-value>)
            return
                (if($cp > 64) then string($cp - 55) else string($cp - 48)),
            ''
            )
        ) mod 97 = 1
    """
    codepoints = [ord(ch) for ch in value]
    res_str_list: list[str] = []
    for codepoint in codepoints:
        if codepoint > 64:
            res_str_list.append(str(codepoint - 55))
        else:
            res_str_list.append(str(codepoint - 48))

    res_int = int("".join(res_str_list))
    return res_int % 97 == 1


################################################################################
# Elementpath Parser Functions (to be removed once done)
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
    val = "".join([ch for ch in val if ch.isnumeric()])
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


################################################################################
# Main Logic
################################################################################


class Element(Generic[T]):
    def __init__(self, namespaces: dict[str, str], parent: Optional["Element"] = None):
        self.namespaces = namespaces
        self.children: List[T] = []
        self._variables: List[Tuple[str, elementpath.Selector]] = []
        self.parent: Optional[Element] = parent
        self.root_name: Optional[str] = parent and parent.root_name

    def add_variable(self, name, path):
        self._variables.append((name, elementpath.Selector(_xpath_normalize_query(path), namespaces=self.namespaces, parser=parser)))

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

        for name, selector in self._variables:
            tt = time()
            ovar_val = selector.select(xml, variables=ovars)
            ovars[name] = ovar_val
            times["evar_old"] += time() - tt

            if name in VARIABLE_TO_IGNORE:
                continue

            path_str = VARIABLE_REPLACE_MAP.get(name, QUERY_REPLACE_MAP.get(selector.path, _xpath_transform_query(selector.path)))
            var_val = try_xpath(xml, path_str, self.namespaces, evars, ovar_val, "evar_meta", name)
            evars[name] = var_val

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
        context = _xpath_normalize_query(context)

        self.context_path = QUERY_REPLACE_MAP.get(context, _xpath_transform_query(context))
        # remove when done
        if self.context_path == "":
            self.context_path = context
        self.context_selector = elementpath.Selector(_xpath_normalize_query(context), namespaces=self.namespaces, parser=parser)

        # List of 4 element tuples, consisting of assert_id, flag, test (selector), message
        self._assertions: List[Tuple[str, str, elementpath.Selector, str]] = []
        self.namespaces.update({"re": "http://exslt.org/regular-expressions"})

    def add_assert(self, assert_id: str, flag: str, test: str, message: str):
        # Before appending, "clean" the test first
        test = _xpath_normalize_query(test)
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
        meta_nodes = try_xpath(xml, self.context_path, self.namespaces, evars_dict, context_nodes, "ctxn_meta", "")
        warning, fatal = [], []

        if stress_mode == "STRESS" and not meta_nodes:
            # Here, they won't run the assert! To have 100% assert coverage we must run all of them
            evars = evars_dict.copy()
            for name, selector in self._variables:
                evars[name] = selector.select(xml, variables=evars)

            for assert_id, flag, selector, message in self._assertions:
                test_str = ASSERT_REPLACE_MAP.get(assert_id, _xpath_transform_query(selector.path))
                _ = try_xpath(dummy_xml, test_str, self.namespaces, evars, False, "stress", assert_id, compare=False)
            pass

        if not isinstance(meta_nodes, list):
            print("skipped current context nodes, fix the context assert!")
            return warning, fatal

        for context_node in meta_nodes:
            # If the rule has additional variable, we evaluate them here.
            ovars = ovars_dict.copy()
            evars = evars_dict.copy()

            if self._variables:
                for name, selector in self._variables:
                    evar_path = VARIABLE_REPLACE_MAP.get(name, QUERY_REPLACE_MAP.get(selector.path, _xpath_transform_query(selector.path)))

                    tt = time()
                    ovar_val = selector.select(xml, item=context_node, variables=ovars)
                    times["var_old"] += time() - tt
                    ovars[name] = ovar_val
                    if isinstance(ovar_val, list) and len(ovar_val) > 1:
                        print(f"ovar_val is a list! (name={name})")
                        # ipdb.set_trace()

                    evar_val = try_xpath(context_node, evar_path, self.namespaces, evars, ovar_val, "var_meta", name)
                    evars[name] = evar_val

            for assert_id, flag, selector, message in self._assertions:
                gid = assert_id
                if assert_id == "PEPPOL-EN16931-R040":
                    # bug on old.py - if you run `xrech2` on peppol schematron (`justpeppol`)
                    new_path = selector.path.replace("then cbc:Amount", "then xs:decimal(cbc:Amount)")
                    selector = elementpath.Selector(new_path, namespaces=selector.namespaces, parser=parser)
                tt = time()
                expected = selector.select(xml, item=context_node, variables=ovars)
                times["assert_old"] += time() - tt

                test_str = ASSERT_REPLACE_MAP.get(assert_id, _xpath_transform_query(selector.path))
                res = try_xpath(context_node, test_str, self.namespaces, evars, expected, "assert_meta", assert_id)
                if not res:
                    assert_message = message if self.root_name == "CEN" else f"[{assert_id}] {message}"
                    if flag == "warning":
                        warning.append(assert_message)
                    elif flag == "fatal":
                        fatal.append(assert_message)

        return warning, fatal


################################################################################
# Script Logic (not to copy to odoo)
################################################################################


def run_schematron(name: str):
    global times
    # if name not in TEST_MAP:
    #     raise Exception("Invalid schematron argument!")
    #
    # schematron_paths = TEST_MAP[name]["schematron_paths"]
    # test_file_path = TEST_MAP[name]["test_file_path"]
    test_file_path, schematron_paths = get_file_and_schematron_paths(sys.argv[1:])

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
        print("all", sum(times.values()))
        print("old", sum(v for k, v in times.items() if "_old" in k))
        print("new", sum(v for k, v in times.items() if "_meta" in k))
        times = {k: 0.0 for k in times}  # reset times for the next schematron


def main():
    to_run = sys.argv[1]
    # if to_run == "saxonche":
    #     saxonche()
    #     return

    if len(sys.argv) > 2:
        global stress_mode
        stress_mode = sys.argv[2].upper()

    tt = time()
    run_schematron(to_run)
    pprint(time() - tt)


if __name__ == "__main__":
    main()

if 2 == 1:
    # To keep the import from deleted by autocomplete
    ipdb.set_trace()

print(to_handle_map)
print(len(to_handle_map))
