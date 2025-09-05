from typing import TypedDict

SCHEMATRON_CEN_PATH = "validation/schematron/CEN-EN16931-UBL.sch"
SCHEMATRON_PEPPOL_PATH = "validation/schematron/PEPPOL-EN16931-UBL.sch"
SCHEMATRON_NLCIUS_PATH = "validation/schematron/SI-UBL-2.0.sch"
SCHEMATRON_EUSR_PATH = "validation/schematron/peppol-end-user-statistics-reporting-1.1.4.sch"
SCHEMATRON_TSR_PATH = "validation/schematron/peppol-transaction-statistics-reporting-1.0.4.sch"
SCHEMATRON_XRECHNUNG_PATH = "validation/schematron/XRechnung-UBL-validation.sch"
SCHEMATRON_AUNZ_1_PATH = "validation/schematron/PINT-jurisdiction-aligned-rules.sch"
SCHEMATRON_AUNZ_2_PATH = "validation/schematron/PINT-UBL-validation-preprocessed.sch"
SCHEMATRON_OIOUBL_INV_PATH = "validation/schematron/OIOUBL_Invoice_Schematron.xml"
SCHEMATRON_OIOUBL_CRN_PATH = "validation/schematron/OIOUBL_CreditNote_Schematron.xml"


class TestMapValue(TypedDict):
    schematron_paths: tuple[str, ...]
    test_file_path: str


SPECIAL_FILE_SCHEMATRON: dict[str, list[str]] = {
    "aunz": [SCHEMATRON_AUNZ_1_PATH, SCHEMATRON_AUNZ_2_PATH],
    "peppol": [SCHEMATRON_CEN_PATH, SCHEMATRON_PEPPOL_PATH],
    "nlcius": [SCHEMATRON_CEN_PATH, SCHEMATRON_NLCIUS_PATH],
    "xrechnung": [SCHEMATRON_CEN_PATH, SCHEMATRON_XRECHNUNG_PATH],
    "eusr": [SCHEMATRON_EUSR_PATH],
    "tsr": [SCHEMATRON_TSR_PATH],
    "all": [SCHEMATRON_CEN_PATH, SCHEMATRON_PEPPOL_PATH, SCHEMATRON_NLCIUS_PATH, SCHEMATRON_EUSR_PATH, SCHEMATRON_TSR_PATH],
    "justcen": [SCHEMATRON_CEN_PATH],
    "justpeppol": [SCHEMATRON_PEPPOL_PATH],
    "justnlcius": [SCHEMATRON_NLCIUS_PATH],
    "justxrechnung": [SCHEMATRON_XRECHNUNG_PATH],
    "justoioublinv": [SCHEMATRON_OIOUBL_INV_PATH],
}


def get_file_and_schematron_paths(args: list[str]) -> tuple[str, list[str]]:
    arg = args[0]
    file_path = f"test_files/{arg}.xml"

    if len(args) >= 2:
        schematron_paths = SPECIAL_FILE_SCHEMATRON[args[1]]
    else:
        schematron_paths = SPECIAL_FILE_SCHEMATRON.get(arg, [SCHEMATRON_CEN_PATH])

    return file_path, schematron_paths


PATH_ROOT_MAP = {
    SCHEMATRON_CEN_PATH: "CEN",
    SCHEMATRON_PEPPOL_PATH: "PEPPOL",
    SCHEMATRON_NLCIUS_PATH: "NLCIUS",
    SCHEMATRON_XRECHNUNG_PATH: "XRECHNUNG",
    SCHEMATRON_AUNZ_1_PATH: "AUNZ1",
    SCHEMATRON_AUNZ_2_PATH: "AUNZ2",
    SCHEMATRON_EUSR_PATH: "EUSR",
    SCHEMATRON_TSR_PATH: "TSR",
}


################################################################################
# Sync everything from this point below with `schematron_lxml_const.py`
################################################################################

GNSMAP = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
    "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
    "cn": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "eusr": "urn:fdc:peppol:end-user-statistics-report:1.1",
    "tsr": "urn:fdc:peppol:transaction-statistics-report:1.0",
    "ubl-creditnote": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "ubl-invoice": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "u": "utils",
    "re": "http://exslt.org/regular-expressions",
}

PEPPOL_CONST_ISO3166 = " AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW 1A XI "
PEPPOL_CONST_ISO4217 = " AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BIF BMD BND BOB BOV BRL BSD BTN BWP BYN BZD CAD CDF CHE CHF CHW CLF CLP CNY COP COU CRC CUC CUP CVE CZK DJF DKK DOP DZD EGP ERN ETB EUR FJD FKP GBP GEL GHS GIP GMD GNF GTQ GYD HKD HNL HRK HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD MAD MDL MGA MKD MMK MNT MOP MRO MUR MVR MWK MXN MXV MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR SBD SCR SDG SEK SGD SHP SLL SOS SRD SSP STN SVC SYP SZL THB TJS TMT TND TOP TRY TTD TWD TZS UAH UGX USD USN UYI UYU UZS VEF VND VUV WST XAF XAG XAU XBA XBB XBC XBD XCD XDR XOF XPD XPF XPT XSU XTS XUA XXX YER ZAR ZMW ZWL "
PEPPOL_CONST_MIMECODE = " application/pdf image/png image/jpeg text/csv application/vnd.openxmlformats-officedocument.spreadsheetml.sheet application/vnd.oasis.opendocument.spreadsheet "
PEPPOL_CONST_UNCL2005 = " 3 35 432 "
PEPPOL_CONST_UNCL5189 = " 41 42 60 62 63 64 65 66 67 68 70 71 88 95 100 102 103 104 105 "
PEPPOL_CONST_UNCL7161 = " AA AAA AAC AAD AAE AAF AAH AAI AAS AAT AAV AAY AAZ ABA ABB ABC ABD ABF ABK ABL ABN ABR ABS ABT ABU ACF ACG ACH ACI ACJ ACK ACL ACM ACS ADC ADE ADJ ADK ADL ADM ADN ADO ADP ADQ ADR ADT ADW ADY ADZ AEA AEB AEC AED AEF AEH AEI AEJ AEK AEL AEM AEN AEO AEP AES AET AEU AEV AEW AEX AEY AEZ AJ AU CA CAB CAD CAE CAF CAI CAJ CAK CAL CAM CAN CAO CAP CAQ CAR CAS CAT CAU CAV CAW CAX CAY CAZ CD CG CS CT DAB DAC DAD DAF DAG DAH DAI DAJ DAK DAL DAM DAN DAO DAP DAQ DL EG EP ER FAA FAB FAC FC FH FI GAA HAA HD HH IAA IAB ID IF IR IS KO L1 LA LAA LAB LF MAE MI ML NAA OA PA PAA PC PL RAB RAC RAD RAF RE RF RH RV SA SAA SAD SAE SAI SG SH SM SU TAB TAC TT TV V1 V2 WH XAA YY ZZZ "
PEPPOL_CONST_UNCL5305 = " AE E S Z G O K L M "
PEPPOL_CONST_EAID = " 0002 0007 0009 0037 0060 0088 0096 0097 0106 0130 0135 0142 0151 0183 0184 0188 0190 0191 0192 0193 0195 0196 0198 0199 0200 0201 0202 0204 0208 0209 0210 0211 0212 0213 0215 0216 0218 0221 0230 9901 9910 9913 9914 9915 9918 9919 9920 9922 9923 9924 9925 9926 9927 9928 9929 9930 9931 9932 9933 9934 9935 9936 9937 9938 9939 9940 9941 9942 9943 9944 9945 9946 9947 9948 9949 9950 9951 9952 9953 9957 9959 "
PEPPOL_CONST_GREEK_GDT = " 1.1 1.6 2.1 2.4 5.1 5.2 "
TSR_CONST_CL_SPIDTYPE = " CertSubjectCN "


# IMPORTANT: replace all asserts that uses these variables
VARIABLE_TO_IGNORE = {
    "greekDocumentType",
    "tokenizedUblIssueDate",
    "ISO3166",
    "ISO4217",
    "MIMECODE",
    "UNCL2005",
    "UNCL5189",
    "UNCL7161",
    "UNCL5305",
    "eaid",
}


ROUND_SUM_KEY_TO_CODE_MAP = {
    "BR-AE-08": "AE",
    "BR-E-08": "E",
    "BR-G-08": "G",
    "BR-IC-08": "K",
    "BR-O-08": "O",
    "BR-Z-08": "Z",
    "aligned-ibrp-z-08-aunz": "Z",
}

WITHIN_ONE_SUM_ASSERT_KEY_TO_CODE_MAP = {
    "BR-IG-08": "L",
    "BR-IP-08": "M",
}

WITHIN_ONE_SUM_EXISTS_ASSERT_KEY_TO_CODE_MAP = {
    "BR-S-08": "S",
}

SLACK_SUM_EXISTS_ASSERT_KEY_TO_CODE_MAP = {
    "aligned-ibrp-s-08-aunz": "S",
}


def _get_br_code_08_sum_str(is_invoice: bool, code: str, with_percent: bool):
    line_element = "InvoiceLine" if is_invoice else "CreditNoteLine"
    if with_percent:
        line_percent_condition = " and number(cac:Item/cac:ClassifiedTaxCategory/cbc:Percent) = number($VAR)"
        allowance_percent_condition = " and cac:TaxCategory/cbc:Percent = $VAR"
    else:
        line_percent_condition = ""
        allowance_percent_condition = ""

    return f"""
    (
        sum(../../../cac:{line_element}[
            cac:Item/cac:ClassifiedTaxCategory
            and normalize-space(cac:Item/cac:ClassifiedTaxCategory/cbc:ID) = '{code}'
            {line_percent_condition}
        ]/cbc:LineExtensionAmount)
        +
        sum(../../../cac:AllowanceCharge[
            cbc:ChargeIndicator = 'true'
            and cac:TaxCategory and normalize-space(cac:TaxCategory/cbc:ID) = '{code}'
            {allowance_percent_condition}
        ]/cbc:Amount)
        -
        sum(../../../cac:AllowanceCharge[
            cbc:ChargeIndicator = 'false'
            and cac:TaxCategory
            and normalize-space(cac:TaxCategory/cbc:ID) = '{code}'
            {allowance_percent_condition}
        ]/cbc:Amount)
    )
    """


BR_CODE_08_ROUND_SUM_ASSERT_MAP = {
    assert_key: f"""
    (
        //cac:InvoiceLine and
        u:round(number(../cbc:TaxableAmount), 2) = u:round({_get_br_code_08_sum_str(True, code, False)}, 2)
    ) or (
        //cac:CreditNoteLine and
        u:round(number(../cbc:TaxableAmount), 2) = u:round({_get_br_code_08_sum_str(False, code, False)}, 2)
    )
    """
    for assert_key, code in ROUND_SUM_KEY_TO_CODE_MAP.items()
}

BR_CODE_08_WITHIN_ONE_SUM_ASSERT_MAP = {
    assert_key: f"""
    u:for_every(
        cbc:Percent,
        "(
            //cac:InvoiceLine
            and ../number(cbc:TaxableAmount) - 1 < {_get_br_code_08_sum_str(True, code, True)}
            and ../number(cbc:TaxableAmount) + 1 > {_get_br_code_08_sum_str(True, code, True)}
        ) or (
            //cac:CreditNoteLine
            and ../number(cbc:TaxableAmount) - 1 < {_get_br_code_08_sum_str(False, code, True)}
            and ../number(cbc:TaxableAmount) + 1 > {_get_br_code_08_sum_str(False, code, True)}
        )"
    )
    """
    for assert_key, code in WITHIN_ONE_SUM_ASSERT_KEY_TO_CODE_MAP.items()
}

BR_CODE_08_WITHIN_ONE_SUM_EXISTS_ASSERT_MAP = {
    assert_key: f"""
    u:for_every(
        cbc:Percent,
        "(
            (
                u:exists(//cac:InvoiceLine[cac:Item/cac:ClassifiedTaxCategory/cbc:ID[normalize-space(.) = '{code}'] and cac:Item/cac:ClassifiedTaxCategory/cbc:Percent = $VAR]/cbc:LineExtensionAmount) or
                u:exists(//cac:AllowanceCharge[cac:TaxCategory/cbc:ID[normalize-space(.)='{code}'] and cac:TaxCategory/cbc:Percent = $VAR]/cbc:Amount)
            )
            and ../cbc:TaxableAmount - 1 < {_get_br_code_08_sum_str(True, code, True)}
            and ../cbc:TaxableAmount + 1 > {_get_br_code_08_sum_str(True, code, True)}
        ) or (
            (
                u:exists(//cac:CreditNoteLine[cac:Item/cac:ClassifiedTaxCategory/cbc:ID[normalize-space(.) = '{code}'] and cac:Item/cac:ClassifiedTaxCategory/cbc:Percent = $VAR]/cbc:LineExtensionAmount) or
                u:exists(//cac:AllowanceCharge[cac:TaxCategory/cbc:ID[normalize-space(.)='{code}'] and cac:TaxCategory/cbc:Percent = $VAR]/cbc:Amount)
            )
            and ../cbc:TaxableAmount - 1 < {_get_br_code_08_sum_str(False, code, True)}
            and ../cbc:TaxableAmount + 1 > {_get_br_code_08_sum_str(False, code, True)}
        )"
    )
    """
    for assert_key, code in WITHIN_ONE_SUM_EXISTS_ASSERT_KEY_TO_CODE_MAP.items()
}

BR_CODE_08_SLACK_SUM_EXISTS_ASSERT_MAP = {
    assert_key: f"""
    u:for_every(
        cbc:Percent,
        "(
            (
                u:exists(//cac:InvoiceLine[cac:Item/cac:ClassifiedTaxCategory/cbc:ID[normalize-space(.) = '{code}'] and cac:Item/cac:ClassifiedTaxCategory/cbc:Percent = $VAR]/cbc:LineExtensionAmount) or
                u:exists(//cac:AllowanceCharge[cac:TaxCategory/cbc:ID[normalize-space(.)='{code}'] and cac:TaxCategory/cbc:Percent = $VAR]/cbc:Amount)
            )
            and u:slack(
                number(../cbc:TaxableAmount),
                {_get_br_code_08_sum_str(True, code, True)},
                1
            )
        ) or (
            (
                u:exists(//cac:CreditNoteLine[cac:Item/cac:ClassifiedTaxCategory/cbc:ID[normalize-space(.) = '{code}'] and cac:Item/cac:ClassifiedTaxCategory/cbc:Percent = $VAR]/cbc:LineExtensionAmount) or
                u:exists(//cac:AllowanceCharge[cac:TaxCategory/cbc:ID[normalize-space(.)='{code}'] and cac:TaxCategory/cbc:Percent = $VAR]/cbc:Amount)
            )
            and u:slack(
                number(../cbc:TaxableAmount),
                {_get_br_code_08_sum_str(False, code, True)},
                1
            )
        )"
    )
    """
    for assert_key, code in SLACK_SUM_EXISTS_ASSERT_KEY_TO_CODE_MAP.items()
}


DUPLICATE_ASSERT_MAP: dict[tuple[str, ...], str] = {
    ################################################################################
    # Duplicate origin: CEN
    ################################################################################
    (
        "BR-29",
        "ibr-029",
    ): "(u:exists(cbc:EndDate) and u:exists(cbc:StartDate) and u:compare_date(cbc:EndDate, '>=', cbc:StartDate)) or not(u:exists(cbc:StartDate)) or not(u:exists(cbc:EndDate))",
    (
        "BR-30",
        "ibr-030",
    ): "(u:exists(cbc:EndDate) and u:exists(cbc:StartDate) and u:compare_date(cbc:EndDate, '>=', cbc:StartDate)) or not(u:exists(cbc:StartDate)) or not(u:exists(cbc:EndDate))",
    ("BR-53", "ibr-053"): "u:for_every(cbc:TaxCurrencyCode, 'u:exists(//cac:TaxTotal/cbc:TaxAmount[@currencyID=$VAR])')",
    (
        "BR-CO-10",
        "ibr-co-10",
    ): "u:round(number(cbc:LineExtensionAmount), 2) = u:if_else(//cac:InvoiceLine, u:round(sum(//cac:InvoiceLine/cbc:LineExtensionAmount), 2), u:round(sum(//cac:CreditNoteLine/cbc:LineExtensionAmount), 2))",
    (
        "BR-CO-11",
        "ibr-co-11",
    ): "u:round(number(cbc:AllowanceTotalAmount), 2) = u:round(sum(../cac:AllowanceCharge[cbc:ChargeIndicator='false']/cbc:Amount), 2) or (not(cbc:AllowanceTotalAmount) and not(../cac:AllowanceCharge[cbc:ChargeIndicator='false']))",
    (
        "BR-CO-12",
        "ibr-co-12",
    ): "u:round(number(cbc:ChargeTotalAmount), 2) = u:round(sum(../cac:AllowanceCharge[cbc:ChargeIndicator='true']/cbc:Amount), 2) or (not(cbc:ChargeTotalAmount) and not(../cac:AllowanceCharge[cbc:ChargeIndicator='true']))",
    (
        "BR-CO-14",
        "ibr-co-14",
    ): "(u:round(number(cbc:TaxAmount), 2) = u:round(sum(cac:TaxSubtotal/cbc:TaxAmount), 2)) or not(boolean(cac:TaxSubtotal))",
    ################################################################################
    # Duplicate origin: PEPPOL
    ################################################################################
    ("PEPPOL-EN16931-F001", "ibr-073"): "string-length(text()) = 10 and u:castable(string(.), 'date')",
    ("DE-R-016", "BR-DE-16"): """
        (not(
          ($BT-95-UBL-Inv = $supportedVATCodes or $BT-95-UBL-CN = $supportedVATCodes) or
          ($BT-102 = $supportedVATCodes) or
          ($BT-151 = $supportedVATCodes)
        ) or
        (cac:TaxRepresentativeParty or $BT-31orBT-32Path))
    """,
    ("DE-R-018", "BR-DE-18"): """
    u:for_every(
        u:tokenize(cac:PaymentTerms/cbc:Note[1], '(\\r?\\n)')[starts-with(normalize-space(.) , '#')],
        "re:match (normalize-space($VAR), '(^|\\r?\\n)#(SKONTO)#TAGE=([0-9]+#PROZENT=[0-9]+\\.[0-9]{2})(#BASISBETRAG=-?[0-9]+\\.[0-9]{2})?#$') and
         re:match (u:tokenize(cac:PaymentTerms/cbc:Note[1], '#.+#')[last()], '^\\s*\\n')"
    )
    """,
    ("DE-R-019", "BR-DE-19"): """
        not(normalize-space(cbc:PaymentMeansCode) = '58') or
        re:match(normalize-space(u:replace(cac:PayeeFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')), '^[A-Z]{2}[0-9]{2}[a-zA-Z0-9]{0,30}$')
        and u:xrechnung_verify_iban(
            concat(
                substring(normalize-space(u:replace(cac:PayeeFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),5),
                u:upper_case(substring(normalize-space(u:replace(cac:PayeeFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),1,2)),
                substring(normalize-space(u:replace(cac:PayeeFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),3,2)
            )
        )
    """,
    ("DE-R-020", "BR-DE-20"): """
        not(normalize-space(cbc:PaymentMeansCode) = '59') or
        re:match(normalize-space(u:replace(cac:PaymentMandate/cac:PayerFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')), '^[A-Z]{2}[0-9]{2}[a-zA-Z0-9]{0,30}$')
        and u:xrechnung_verify_iban(
            concat(
                substring(normalize-space(u:replace(cac:PaymentMandate/cac:PayerFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),5),
                u:upper_case(substring(normalize-space(u:replace(cac:PaymentMandate/cac:PayerFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),1,2)),
                substring(normalize-space(u:replace(cac:PaymentMandate/cac:PayerFinancialAccount/cbc:ID, '([ \\n\\r\\t\\s])', '')),3,2)
            )
        )
    """,
    ("DE-R-027", "BR-DE-27"): "u:exists(re:match(normalize-space(cbc:Telephone), $XR-TELEPHONE-REGEX))",
    ("DE-R-028", "BR-DE-28"): "u:exists(re:match(normalize-space(cbc:ElectronicMail), $XR-EMAIL-REGEX))",
}

EXPANDED_DUPLICATE_ASSERT_MAP = {key: common_rule for duplicate_keys, common_rule in DUPLICATE_ASSERT_MAP.items() for key in duplicate_keys}


# Map of variable_name -> xpath1 query
VARIABLE_REPLACE_MAP = {
    ################################################################################
    # PEPPOL
    ################################################################################
    "profile": """
        u:if_else(
            /*/cbc:ProfileID and re:match(normalize-space(/*/cbc:ProfileID), 'urn:fdc:peppol.eu:2017:poacc:billing:([0-9]{2}):1.0'),
            u:tokenize(normalize-space(/*/cbc:ProfileID), ':')[7],
            'Unknown'
        )
    """,
    "customerCountry": """
        u:if_else(
            /*/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2)],
            u:upper_case(normalize-space(substring(/*/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID[1], 1, 2))),
            u:if_else(
                /*/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode,
                u:upper_case(normalize-space(/*/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)),
                'XX'
            )
        )
    """,
    "accountingSupplierCountry": """
        u:if_else(
            /*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2)],
            u:upper_case(normalize-space(substring(/*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID[1], 1, 2))),
            u:if_else(
                /*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode,
                u:upper_case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)),
                'XX'
            )
        )
    """,
    "supplierCountryIsNL": "(u:upper_case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)) = 'NL')",
    "customerCountryIsNL": "(u:upper_case(normalize-space(/*/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)) = 'NL')",
    "taxRepresentativeCountryIsNL": "(u:upper_case(normalize-space(/*/cac:TaxRepresentativeParty/cac:PostalAddress/cac:Country/cbc:IdentificationCode)) = 'NL')",
    ################################################################################
    # XRECHNUNG
    ################################################################################
    "supportedVATCodes": "u:tokenize('S Z E AE K G L M', ' ')",
    "supportedInvAndCNTypeCodes": "u:tokenize('326 380 384 389 381 875 876 877', ' ')",
    ################################################################################
    # AU-NZ PINT
    ################################################################################
    "buyerCountry": """
        u:if_else(
            /*/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode,
            u:upper_case(normalize-space(/*/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)),
            'XX'
        )
    """,
    ################################################################################
    # Rule/Assert Level Variables
    ################################################################################
    "lineExtensionAmount": "u:if_else(cbc:LineExtensionAmount, number(cbc:LineExtensionAmount), 0)",
    "priceAmount": "u:if_else(cac:Price/cbc:PriceAmount, number(cac:Price/cbc:PriceAmount), 0)",
    "baseQuantity": "u:if_else((cac:Price/cbc:BaseQuantity and number(cac:Price/cbc:BaseQuantity) != 0), number(cac:Price/cbc:BaseQuantity), 1)",
    "allowancesTotal": """
        u:if_else(
            cac:AllowanceCharge[cbc:ChargeIndicator = 'false'],
            u:round(sum(cac:AllowanceCharge[cbc:ChargeIndicator = 'false']/cbc:Amount), 2),
            0
        )
    """,
    "chargesTotal": """
        u:if_else(
            cac:AllowanceCharge[cbc:ChargeIndicator = 'true'],
            u:round(sum(cac:AllowanceCharge[cbc:ChargeIndicator = 'true']/cbc:Amount), 2),
            0
        )
    """,
}


QUERY_CEN_CODES = ("AE", "E", "G", "K", "L", "M", "O", "S", "Z")

QUERY_CEN_CODE_TAXTOTAL = {
    f"/*/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[normalize-space(cbc:ID) = '{code}'][cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT']": f"""
        /*/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[
            normalize-space(cbc:ID) = '{code}' and
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'
        ]
    """
    for code in QUERY_CEN_CODES
}
QUERY_CEN_CODE_ALLOWANCE_CHARGE_FALSE = {
    f"//cac:AllowanceCharge[cbc:ChargeIndicator=false()]/cac:TaxCategory[normalize-space(cbc:ID)='{code}'][cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT']": f"""
        //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[
            normalize-space(cbc:ID)='{code}' and
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'
        ]
    """
    for code in QUERY_CEN_CODES
}
QUERY_CEN_CODE_ALLOWANCE_CHARGE_TRUE = {
    f"//cac:AllowanceCharge[cbc:ChargeIndicator=true()]/cac:TaxCategory[normalize-space(cbc:ID)='{code}'][cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT']": f"""
        //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[
            normalize-space(cbc:ID)='{code}' and
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'
        ]
    """
    for code in QUERY_CEN_CODES
}
QUERY_CEN_CODE_INVOICELINE = {
    f"//cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory[normalize-space(cbc:ID) = '{code}'][cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT'] | //cac:CreditNoteLine/cac:Item/cac:ClassifiedTaxCategory[normalize-space(cbc:ID) = '{code}'][cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT']": f"""
        //cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory[
            normalize-space(cbc:ID) = '{code}' and
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'
        ]
        |
        //cac:CreditNoteLine/cac:Item/cac:ClassifiedTaxCategory[
            normalize-space(cbc:ID) = '{code}' and
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'
        ]
    """
    for code in QUERY_CEN_CODES
}


# Map of xpath2 query -> xpath1 query
# Only used for context queries and duplicate variable names with different queries
# To make it consistent, all to-be-translated query must be stripped and any multiple whitespaces must be replaced with a single whitespace
QUERY_REPLACE_MAP = {
    ################################################################################
    # CEN
    ################################################################################
    **QUERY_CEN_CODE_TAXTOTAL,
    **QUERY_CEN_CODE_ALLOWANCE_CHARGE_FALSE,
    **QUERY_CEN_CODE_ALLOWANCE_CHARGE_TRUE,
    **QUERY_CEN_CODE_INVOICELINE,
    "//cac:PartyTaxScheme[cac:TaxScheme/normalize-space(upper-case(cbc:ID))='VAT']": "//cac:PartyTaxScheme[cac:TaxScheme and u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT']",
    "//*[ends-with(name(), 'Amount') and not(ends-with(name(),'PriceAmount')) and not(ancestor::cac:Price/cac:AllowanceCharge)]": """
    //*[
        substring(name(), string-length(name()) - 5) = 'Amount' and
        not(substring(name(), string-length(name()) - 10) = 'PriceAmount') and
        not(ancestor::cac:Price/cac:AllowanceCharge)
    ]
    """,
    "//*[ends-with(name(), 'BinaryObject')]": "//*[substring(name(), string-length(name()) - 11) = 'BinaryObject']",
    ################################################################################
    # PEPPOL
    ################################################################################
    "//cac:PaymentMeans[some $code in tokenize('49 59', '\\s') satisfies normalize-space(cbc:PaymentMeansCode) = $code]": "//cac:PaymentMeans[contains(' 49 59 ', concat(' ', normalize-space(cbc:PaymentMeansCode), ' '))]",
    "//cac:AccountingSupplierParty/cac:Party[cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2) = 'SE']": "//cac:AccountingSupplierParty/cac:Party[cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2) = 'SE']]",
    "//cac:TaxCategory[//cac:AccountingSupplierParty/cac:Party[cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2) = 'SE'] and cbc:ID = 'S'] | //cac:ClassifiedTaxCategory[//cac:AccountingSupplierParty/cac:Party[cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2) = 'SE'] and cbc:ID = 'S']": """
    //cac:TaxCategory[
        //cac:AccountingSupplierParty/cac:Party[
            cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and
            cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2) = 'SE']
        ] and
        cbc:ID = 'S'
    ] |
    //cac:ClassifiedTaxCategory[
        //cac:AccountingSupplierParty/cac:Party[
            cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'SE' and
            cac:PartyTaxScheme[
                cac:TaxScheme/cbc:ID = 'VAT' and
                substring(cbc:CompanyID, 1, 2) = 'SE'
            ]
        ] and
        cbc:ID = 'S'
    ]
    """,
    # Peppol German Contexts
    "//(/ubl-invoice:Invoice | /ubl-creditnote:CreditNote)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:AccountingSupplierParty | /ubl-creditnote:CreditNote/cac:AccountingSupplierParty)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:AccountingSupplierParty[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:AccountingSupplierParty[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress | /ubl-creditnote:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact | /ubl-creditnote:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:Contact)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:Contact[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress | /ubl-creditnote:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PostalAddress[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address | /ubl-creditnote:CreditNote/cac:Delivery/cac:DeliveryLocation/cac:Address)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:Delivery/cac:DeliveryLocation/cac:Address[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:Delivery/cac:DeliveryLocation/cac:Address[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:PaymentMeans[cbc:PaymentMeansCode = (30,58)] | /ubl-creditnote:CreditNote/cac:PaymentMeans[cbc:PaymentMeansCode = (30,58)])[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:PaymentMeans[cbc:PaymentMeansCode = 30 or cbc:PaymentMeansCode = 58][$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:PaymentMeans[cbc:PaymentMeansCode = 30 or cbc:PaymentMeansCode = 58][$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:PaymentMeans[cbc:PaymentMeansCode = (48,54,55)] | /ubl-creditnote:CreditNote/cac:PaymentMeans[cbc:PaymentMeansCode = (48,54,55)])[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:PaymentMeans[contains(' 48 54 55 ', concat(' ', cbc:PaymentMeansCode, ' '))][$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:PaymentMeans[contains(' 48 54 55 ', concat(' ', cbc:PaymentMeansCode, ' '))][$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:PaymentMeans[cbc:PaymentMeansCode = 59] | /ubl-creditnote:CreditNote/cac:PaymentMeans[cbc:PaymentMeansCode = 59])[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:PaymentMeans[cbc:PaymentMeansCode = 59][$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:PaymentMeans[cbc:PaymentMeansCode = 59][$supplierCountryIsDE and $customerCountryIsDE]
    """,
    "//(/ubl-invoice:Invoice/cac:TaxTotal/cac:TaxSubtotal | /ubl-creditnote:CreditNote/cac:TaxTotal/cac:TaxSubtotal)[$supplierCountryIsDE and $customerCountryIsDE]": """
        //ubl-invoice:Invoice/cac:TaxTotal/cac:TaxSubtotal[$supplierCountryIsDE and $customerCountryIsDE] |
        //ubl-creditnote:CreditNote/cac:TaxTotal/cac:TaxSubtotal[$supplierCountryIsDE and $customerCountryIsDE]
    """,
    ################################################################################
    # XRECHNUNG
    ################################################################################
    "/ubl:Invoice/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = ('30','58')] | /cn:CreditNote/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = ('30','58')]": """
        /ubl:Invoice/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = u:tokenize('30 58', ' ')] |
        /cn:CreditNote/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = u:tokenize('30 58', ' ')]
    """,
    "/ubl:Invoice/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = ('48','54','55')] | /cn:CreditNote/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = ('48','54','55')]": """
        /ubl:Invoice/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = u:tokenize('48 54 55', ' ')] |
        /cn:CreditNote/cac:PaymentMeans[normalize-space(cbc:PaymentMeansCode) = u:tokenize('48 54 55', ' ')]
    """,
    ################################################################################
    # AU-NZ PINT
    ################################################################################
    # For some reason, AU-NZ PINT schematron have a few duplicated assert tests
    # 'aligned-ibrp-054', 'aligned-ibrp-055'
    "not(cbc:MultiplierFactorNumeric and cbc:BaseAmount) or u:slack(if (cbc:Amount) then cbc:Amount else 0, (xs:decimal(cbc:BaseAmount) * xs:decimal(cbc:MultiplierFactorNumeric)) div 100, 0.02)": """
        not(cbc:MultiplierFactorNumeric and cbc:BaseAmount)
        or
        u:slack(
            u:if_else(cbc:Amount, number(cbc:Amount), 0),
            (number(cbc:BaseAmount) * number(cbc:MultiplierFactorNumeric)) div 100,
            0.02
        )
    """,
    ################################################################################
    # Duplicated Variable Names
    ################################################################################
    # "quantity" (from "cac:InvoiceLine | cac:CreditNoteLine")
    "if (/ubl-invoice:Invoice) then (if (cbc:InvoicedQuantity) then xs:decimal(cbc:InvoicedQuantity) else 1) else (if (cbc:CreditedQuantity) then xs:decimal(cbc:CreditedQuantity) else 1)": """
        u:if_else(
            /ubl-invoice:Invoice,
            u:if_else(cbc:InvoicedQuantity, number(cbc:InvoicedQuantity), 1),
            u:if_else(cbc:CreditedQuantity, number(cbc:CreditedQuantity), 1)
        )
    """,
    # "quantity" (from "cac:Price/cbc:BaseQuantity[@unitCode]")
    "if (/ubl-invoice:Invoice) then ../../cbc:InvoicedQuantity else ../../cbc:CreditedQuantity": """
        u:if_else(
            /ubl-invoice:Invoice,
            ../../cbc:InvoicedQuantity,
            ../../cbc:CreditedQuantity
        )
    """,
    # "supplierCountry" (from PEPPOL)
    "if (/*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2)) then upper-case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2))) else if (/*/cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2)) then upper-case(normalize-space(/*/cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/substring(cbc:CompanyID, 1, 2))) else if (/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode) then upper-case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)) else 'XX'": """
        u:if_else(
            /*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2)],
            u:upper_case(normalize-space(substring(/*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID[1], 1, 2))),
            u:if_else(
                /*/cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT' and substring(cbc:CompanyID, 1, 2)],
                u:upper_case(normalize-space(substring(/*/cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID[1], 1, 2))),
                u:if_else(
                    /*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode,
                    u:upper_case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)),
                    'XX'
                )
            )
        )
    """,
    # "supplierCountry" (from NLCIUS)
    "if (/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode) then upper-case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)) else 'XX'": """
        u:if_else(
            /*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode,
            u:upper_case(normalize-space(/*/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode)),
            'XX'
        )

    """,
}


# Map of assert_id -> xpath1 query
ASSERT_REPLACE_MAP = {
    **EXPANDED_DUPLICATE_ASSERT_MAP,
    **BR_CODE_08_ROUND_SUM_ASSERT_MAP,
    **BR_CODE_08_WITHIN_ONE_SUM_ASSERT_MAP,
    **BR_CODE_08_WITHIN_ONE_SUM_EXISTS_ASSERT_MAP,
    **BR_CODE_08_SLACK_SUM_EXISTS_ASSERT_MAP,
    ################################################################################
    # CEN
    ################################################################################
    # **CEN_COMMON_RULES,
    "BR-AE-01": """
        (
            (
                u:exists(//cac:TaxCategory[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:ID[normalize-space() = 'AE'])
                or
                u:exists(//cac:ClassifiedTaxCategory[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:ID[normalize-space() = 'AE'])
            )
            and
            (
                count(
                cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:ID[normalize-space() = 'AE']
                ) = 1
            )
        )
        or
        (
          not(//cac:TaxCategory[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:ID[normalize-space() = 'AE'])
          and
          not(//cac:ClassifiedTaxCategory[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:ID[normalize-space() = 'AE'])
        )
    """,
    "BR-AE-02": """
        (
            u:exists(
                //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'AE'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
            )
            and (
                u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
                or u:exists(
                    //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
                )
            )
            and (
                u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
                or u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID)
            )
        )
        or not(
            u:exists(
                //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'AE'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
            )
        )
    """,
    "BR-AE-03": """
    (
        u:exists(//cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[normalize-space(cbc:ID) = 'AE'][cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']])
        and
        (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or
            u:exists(//cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:CompanyID)
        )
        and
        (
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']]/cbc:CompanyID)
            or
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID)
        )
    )
    or not(
        u:exists(//cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[normalize-space(cbc:ID) = 'AE'][cac:TaxScheme[normalize-space(u:upper_case(cbc:ID)) = 'VAT']])
    )
    """,
    "BR-AE-04": """
    (
        u:exists(//cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'AE'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']])
        and
        (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or
            u:exists(//cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and
        (
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID)
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'AE'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-CO-15": """
    u:for_every(
        cbc:DocumentCurrencyCode,
        "(count(cac:TaxTotal/cbc:TaxAmount[@currencyID=$VAR]) = 1)
         and
         (u:round(number(cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount), 2) =
          u:round(cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount + cac:TaxTotal/cbc:TaxAmount[@currencyID=$VAR], 2))"
    )
    """,
    "BR-E-01": """
    (
        (
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'E']
            )
            or u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'E']
            )
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'E']
        ) = 1
    )
    or (
        not(
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'E']
            )
        )
        and not(
            u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'E']
            )
        )
    )
    """,
    "BR-E-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-E-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-E-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='E'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-G-01": """
    (
        (
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'G']
            )
            or u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'G']
            )
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'G']
        ) = 1
    )
    or (
        not(
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'G']
            )
        )
        and not(
            u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'G']
            )
        )
    )
    """,
    "BR-G-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-G-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-G-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='G'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-IC-01": """
    (
        (
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
            )
            or u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
            )
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
        ) = 1
    )
    or (
        not(
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
            )
        )
        and not(
            u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
            )
        )
    )
    """,
    "BR-IC-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'K'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
        and u:exists(
            //cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'K'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-IC-03": """
    (
        u:exists(
            //cac:allowancecharge[cbc:chargeindicator='false']/cac:taxcategory[cbc:id[normalize-space(.) = 'k'] and cac:taxscheme/cbc:id[normalize-space(u:upper_case(.))='vat']]
        )
        and (
            u:exists(//cac:accountingsupplierparty/cac:party/cac:partytaxscheme[cac:taxscheme/cbc:id[normalize-space(u:upper_case(.)) = 'vat']]/cbc:companyid)
            or u:exists(
                //cac:taxrepresentativeparty/cac:partytaxscheme[cac:taxscheme/cbc:id[normalize-space(u:upper_case(.)) = 'vat']]/cbc:companyid
            )
        )
        and u:exists(
            //cac:accountingcustomerparty/cac:party/cac:partytaxscheme[cac:taxscheme/cbc:id[normalize-space(u:upper_case(.)) = 'vat']]/cbc:companyid
        )
    )
    or not(
        u:exists(
            //cac:allowancecharge[cbc:chargeindicator='false']/cac:taxcategory[cbc:id[normalize-space(.) = 'k'] and cac:taxscheme/cbc:id[normalize-space(u:upper_case(.))='vat']]
        )
    )
    """,
    "BR-IC-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'K'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
        and u:exists(
            //cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'K'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-IC-11": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
        )
        and (string-length(cac:Delivery/cbc:ActualDeliveryDate) > 1 or boolean(cac:InvoicePeriod/*))
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
        )
    )
    """,
    "BR-IC-12": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
        )
        and string-length(cac:Delivery/cac:DeliveryLocation/cac:Address/cac:Country/cbc:IdentificationCode) > 1
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'K']
        )
    )
    """,
    "BR-IG-01": """
    (
        (
            count(//cac:AllowanceCharge/cac:TaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']])
            +
            count(//cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']])
        ) > 0
        and
        count(cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cbc:ID = 'L']) > 0
    ) or (
        (
            count(//cac:AllowanceCharge/cac:TaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]) + count(//cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']])
        ) = 0 and count(cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
    ) = 0
    )
    """,
    "BR-IG-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-IG-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-IG-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='L'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-IP-01": """
    (
        (
            count(//cac:AllowanceCharge/cac:TaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]) + count(//cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']])
        ) > 0 and count(cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cbc:ID = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']) > 0
    ) or (
        (
            count(//cac:AllowanceCharge/cac:TaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]) + count(//cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']])
        ) = 0 and count(cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
    ) = 0
    )
    """,
    "BR-IP-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-IP-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-IP-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='M'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-O-01": """
    (
        (
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
            )
            or u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
            )
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        ) = 1
    )
    or (
        not(
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
            )
        )
        and not(
            u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
            )
        )
    )
    """,
    "BR-O-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and not(
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-O-03": """
    (
        u:exists(
            (/ubl:Invoice|/cn:CreditNote)/cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and not(
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
    )
    or not(
        u:exists(
            (/ubl:Invoice|/cn:CreditNote)/cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-O-04": """
    (
        u:exists(
            (/ubl:Invoice|/cn:CreditNote)/cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and not(
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
        and not(
            u:exists(//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID)
        )
    )
    or not(
        u:exists(
            (/ubl:Invoice|/cn:CreditNote)/cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-O-11": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cbc:ID[normalize-space(.)!= 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        ) = 0
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
    )
    """,
    "BR-O-12": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
        and count(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.)!= 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        ) = 0
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
    )
    """,
    "BR-O-13": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
        and count(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)!= 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        ) = 0
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
    )
    """,
    "BR-O-14": """
    (
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
        and count(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)!= 'O'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        ) = 0
    )
    or not(
        u:exists(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'O']
        )
    )
    """,
    "BR-S-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-S-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-S-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='S'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-Z-01": """
    (
        (
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'Z']
            )
            or u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'Z']
            )
        )
        and count(
            cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'Z']
        ) = 1
    )
    or (
        not(
            u:exists(
                //cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'Z']
            )
        )
        and not(
            u:exists(
                //cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(.)='VAT'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.) = 'Z']
            )
        )
    )
    """,
    "BR-Z-02": """
    (
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:ClassifiedTaxCategory[cbc:ID[normalize-space(.) = 'Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]
        )
    )
    """,
    "BR-Z-03": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.)='Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='false']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-Z-04": """
    (
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.)='Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
        and (
            u:exists(//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID)
            or u:exists(
                //cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.)) = 'VAT']]/cbc:CompanyID
            )
        )
    )
    or not(
        u:exists(
            //cac:AllowanceCharge[cbc:ChargeIndicator='true']/cac:TaxCategory[cbc:ID[normalize-space(.) = 'Z'] and cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]
        )
    )
    """,
    "BR-CO-04": """
        cac:Item/cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID
    """,
    "BR-CO-26": """
        u:exists(cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:CompanyID) or u:exists(cac:Party/cac:PartyIdentification/cbc:ID) or u:exists(cac:Party/cac:PartyLegalEntity/cbc:CompanyID)
    """,
    "BR-47": """
        u:exists(cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID)
    """,
    "BR-48": """
        u:exists(cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent) or (cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:ID[normalize-space(.)='O'])
    """,
    "BR-NL-1": "(contains(concat(' ', u:string_join(cac:PartyLegalEntity/cbc:CompanyID/@schemeID, ' '), ' '), ' 0106 ') or contains(concat(' ', u:string_join(cac:PartyLegalEntity/cbc:CompanyID/@schemeID, ' '), ' '), ' 0190 ')) and (normalize-space(cac:PartyLegalEntity/cbc:CompanyID) != '')",
    "BR-NL-10": "(not(//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode = 'NL') or contains(concat(' ', u:string_join(//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID/@schemeID, ' '), ' '), ' 0106 ') or contains(concat(' ', u:string_join(//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID/@schemeID, ' '), ' '), ' 0190 ') ) and (not(cbc:CompanyID) or (normalize-space(cbc:CompanyID) != ''))",
    "BR-CO-17": """
    (
        round(cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent) = 0 and round(cbc:TaxAmount) = 0
    ) or (
        round(cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent)!= 0 and (
            u:abs(cbc:TaxAmount) - 1 < u:round(u:abs(cbc:TaxableAmount) * (cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent div 100), 2) and u:abs(cbc:TaxAmount) + 1 > u:round(u:abs(cbc:TaxableAmount) * (cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent div 100), 2)
        )
    ) or (
        not(
            u:exists(
                cac:TaxCategory[cac:TaxScheme/cbc:ID[normalize-space(u:upper_case(.))='VAT']]/cbc:Percent
            )
        ) and round(cbc:TaxAmount) = 0
    )
    """,
    "BR-S-09": """
    (
        u:abs(../cbc:TaxAmount) - 1 < u:round((u:abs(../cbc:TaxableAmount) * (cbc:Percent div 100)), 2)
    ) and (
        u:abs(../cbc:TaxAmount) + 1 > u:round((u:abs(../cbc:TaxableAmount) * (cbc:Percent div 100)), 2)
    )
    """,
    "UBL-SR-12": """
        count(cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[u:upper_case(.)='VAT']]/cbc:CompanyID) <= 1
    """,
    "UBL-SR-13": """
        count(cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[u:upper_case(.)!='VAT']]/cbc:CompanyID) <= 1
    """,
    "UBL-SR-18": """
        count(cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID[u:upper_case(.)='VAT']]/cbc:CompanyID) <= 1
    """,
    #
    "BR-IG-09": """
    (
        u:abs(number(../cbc:TaxAmount)) - 1 < u:round(
            u:abs(number(../cbc:TaxableAmount)) * (number(cbc:Percent) div 100),
            2
        )
    ) and (
        u:abs(number(../cbc:TaxAmount)) + 1 > u:round(
            u:abs(number(../cbc:TaxableAmount)) * (number(cbc:Percent) div 100),
            2
        )
    )
    """,
    "BR-IP-09": """
    (
        u:abs(number(../cbc:TaxAmount)) - 1 < u:round(
            u:abs(number(../cbc:TaxableAmount)) * (number(cbc:Percent) div 100),
            2
        )
    ) and (
        u:abs(number(../cbc:TaxAmount)) + 1 > u:round(
            u:abs(number(../cbc:TaxableAmount)) * (number(cbc:Percent) div 100),
            2
        )
    )
    """,
    "BR-32": "u:exists(cac:TaxCategory[cac:TaxScheme and u:upper_case(normalize-space(cac:TaxScheme/cbc:ID))='VAT'])",
    "BR-37": "u:exists(cac:TaxCategory[cac:TaxScheme and u:upper_case(normalize-space(cac:TaxScheme/cbc:ID)) = 'VAT'])",
    "BR-56": "u:exists(cac:PartyTaxScheme[cac:TaxScheme and (normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'VAT')]/cbc:CompanyID)",
    ################################################################################
    # PEPPOL
    ################################################################################
    # FIXME: [PEPPOL-COMMON-R043] find out why u:mod97-0208(...) fails when validating Belgian company number
    "PEPPOL-COMMON-R043": "u:exists(re:match(normalize-space(), '^[0-9]{10}$'))",
    "PEPPOL-EN16931-CL002": f"contains('{PEPPOL_CONST_UNCL5189}', concat(' ', text(), ' '))",
    "PEPPOL-EN16931-CL003": f"contains('{PEPPOL_CONST_UNCL7161}', concat(' ', text(), ' '))",
    "PEPPOL-EN16931-CL006": f"contains('{PEPPOL_CONST_UNCL2005}', concat(' ', text(), ' '))",
    "PEPPOL-EN16931-P0101": "$profile != '01' or (contains(' 381 396 81 83 532 ', concat(' ', text(), ' ')))",
    "PEPPOL-EN16931-R054": "count(cac:TaxTotal[not(cac:TaxSubtotal)]) = u:if_else(//cbc:TaxCurrencyCode, 1, 0)",
    "PEPPOL-EN16931-CL001": f"contains('{PEPPOL_CONST_MIMECODE}', concat(' ', @mimeCode, ' '))",
    "PEPPOL-EN16931-CL007": f"contains('{PEPPOL_CONST_ISO4217}', concat(' ', @currencyID, ' '))",
    "PEPPOL-EN16931-P0100": "$profile != '01' or contains(' 71 80 82 84 102 218 219 331 380 382 383 386 388 393 395 553 575 623 780 817 870 875 876 877 ', concat(' ', normalize-space(text()), ' '))",
    "PEPPOL-EN16931-CL008": f"contains('{PEPPOL_CONST_EAID}', concat(' ', @schemeID, ' '))",
    "PEPPOL-EN16931-R040": "not(cbc:MultiplierFactorNumeric and cbc:BaseAmount) or u:slack(u:if_else(cbc:Amount, number(cbc:Amount), 0), (number(cbc:BaseAmount) * number(cbc:MultiplierFactorNumeric)) div 100, 0.02)",
    "PEPPOL-EN16931-R110": "u:compare_date(text(), '>=' ,../../../cac:InvoicePeriod/cbc:StartDate)",
    "PEPPOL-EN16931-R111": "u:compare_date(text(), '<=' ,../../../cac:InvoicePeriod/cbc:EndDate)",
    "NO-R-001": """
    (
        cac:PartyTaxScheme[
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID)) = 'VAT' and
            substring(cbc:CompanyID, 1, 2) = 'NO' and
            re:match(substring(cbc:CompanyID, 3), '^[0-9]{9}MVA$') and
            u:mod11(substring(cbc:CompanyID, 3, 9))
        ]
    ) or not(
        cac:PartyTaxScheme[
            cac:TaxScheme and
            u:upper_case(normalize-space(cac:TaxScheme/cbc:ID)) = 'VAT' and
            substring(cbc:CompanyID, 1, 2) = 'NO'
        ]
    )
    """,
    "GR-R-001-2": """
        string-length(normalize-space($IdSegments[1])) = 9 and
        u:TinVerification($IdSegments[1]) and
        (
            $IdSegments[1] = substring(string(/*/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID), 3, 9) or
            $IdSegments[1] = substring(string(/*/cac:TaxRepresentativeParty/cac:PartyTaxScheme[cac:TaxScheme/cbc:ID = 'VAT']/cbc:CompanyID), 3, 9)
        )
    """,
    "GR-R-001-5": f"string-length(normalize-space($IdSegments[4]))>0 and contains('{PEPPOL_CONST_GREEK_GDT}', concat(' ', $IdSegments[4], ' '))",
    "IS-R-008": """
    (
        cac:AdditionalDocumentReference[cbc:DocumentDescription = 'EINDAGI' and string-length(cbc:ID) = 10] and
        u:castable(substring(string(cac:AdditionalDocumentReference[cbc:DocumentDescription = 'EINDAGI']/cbc:ID),1,10), 'date')
    ) or
    not(
        cac:AdditionalDocumentReference[cbc:DocumentDescription = 'EINDAGI']
    )
    """,
    ################################################################################
    # AU-NZ PINT
    ################################################################################
    "aligned-ibrp-022": "count(cac:TaxTotal[not(cac:TaxSubtotal)]) = u:if_else(cbc:TaxCurrencyCode, 1, 0)",
    "aligned-ibrp-032-aunz": """
        u:exists(
            cac:TaxCategory[
                cac:TaxScheme/cbc:ID and
                normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST'
            ]/cbc:ID
        )
        or not(parent::ubl:Invoice|parent::cn:CreditNote)
    """,
    "aligned-ibrp-sr-12-aunz": """
        (count(cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[u:upper_case(cac:TaxScheme/cbc:ID)='GST']/cbc:CompanyID) <= 1)
    """,
    "aligned-ibrp-sr-13-aunz": """
        (count(cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme[u:upper_case(cac:TaxScheme/cbc:ID)!='GST']/cbc:CompanyID) <= 1)
    """,
    "aligned-ibrp-048-aunz": """
        u:exists(
            cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:Percent
        )
        or (
            cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:ID and
            normalize-space(
                cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:ID
            ) = 'O'
        )
    """,
    "aligned-ibrp-050-aunz": """
        (cac:Item/cac:ClassifiedTaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:ID)
    """,
    "aligned-ibrp-051-aunz": """
        (
            round(number(cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:Percent)) = 0 and
            round(number(cbc:TaxAmount)) = 0
        )
        or
        (
            round(number(cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:Percent)) != 0 and
            u:slack(
                u:abs(number(cbc:TaxAmount)),
                u:round(
                    u:abs(number(cbc:TaxableAmount)) *
                    (number(cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:Percent) div 100),
                    2
                ),
                1
            )
        )
        or
        (
            not(u:exists(number(cac:TaxCategory[cac:TaxScheme/cbc:ID and normalize-space(u:upper_case(cac:TaxScheme/cbc:ID)) = 'GST']/cbc:Percent))) and
            round(number(cbc:TaxAmount)) = 0
        )
    """,
    "ibr-co-15": """
        cac:TaxTotal/cbc:TaxIncludedIndicator = true()
        or
        number(cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount) = u:round(
            number(cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount) + number(cac:TaxTotal/cbc:TaxAmount[@currencyID=/*/cbc:DocumentCurrencyCode]),
            2
        )
    """,
    "ibr-085": """
        u:compare_date(cbc:StartDate, '>=', ../../cac:InvoicePeriod/cbc:StartDate) or not(cbc:StartDate) or not(../../cac:InvoicePeriod/cbc:StartDate)
    """,
    "ibr-086": """
        u:compare_date(cbc:EndDate, '<=', ../../cac:InvoicePeriod/cbc:EndDate) or not(cbc:EndDate) or not(../../cac:InvoicePeriod/cbc:EndDate)
    """,
    ################################################################################
    # EUSR
    ################################################################################
    "SCH-EUSR-03": "$empty or u:max(eusr:Subset/eusr:SendingEndUsers) <= number(eusr:FullSet/eusr:SendingEndUsers)",
    "SCH-EUSR-04": "$empty or u:max(eusr:Subset/eusr:ReceivingEndUsers) <= number(eusr:FullSet/eusr:ReceivingEndUsers)",
    "SCH-EUSR-16": "u:exists(re:match(normalize-space(eusr:ReportPeriod/eusr:StartDate), '^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}$'))",
    "SCH-EUSR-17": "u:exists(re:match(normalize-space(eusr:ReportPeriod/eusr:EndDate), '^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}$'))",
    "SCH-EUSR-18": "u:compare_date(eusr:ReportPeriod/eusr:EndDate, '>=', eusr:ReportPeriod/eusr:StartDate)",
    "SCH-EUSR-22": "$empty or u:max(eusr:Subset/eusr:SendingOrReceivingEndUsers) <= number(eusr:FullSet/eusr:SendingOrReceivingEndUsers)",
    "SCH-EUSR-33": "u:for_every(eusr:Subset, 'number($VAR/eusr:SendingOrReceivingEndUsers) <= number($VAR/eusr:SendingEndUsers + $VAR/eusr:ReceivingEndUsers)')",
    "SCH-EUSR-34": "u:for_every(eusr:Subset, 'number($VAR/eusr:SendingOrReceivingEndUsers) >= number($VAR/eusr:SendingEndUsers)')",
    "SCH-EUSR-35": "u:for_every(eusr:Subset, 'number($VAR/eusr:SendingOrReceivingEndUsers) >= number($VAR/eusr:ReceivingEndUsers)')",
    "SCH-EUSR-36": "u:for_every(eusr:Subset, 'number($VAR/eusr:SendingOrReceivingEndUsers) > 0')",
    "SCH-EUSR-40": "u:id_SCH_EUSR_40()",
    ################################################################################
    # TSR
    ################################################################################
    "SCH-TSR-06": """
    u:for_every(
        tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key,
        \"count(tsr:Subtotal[normalize-space(@type) = 'PerTP']/tsr:Key[concat(normalize-space(@schemeID),'::',normalize-space(.)) = concat(normalize-space($VAR/@schemeID),'::',normalize-space($VAR))]) = 1\"
    )
    """,
    "SCH-TSR-19": "u:exists(re:match(normalize-space(.), $re_seatid))",
    "SCH-TSR-28": f"u:for_every(tsr:Key[normalize-space(@metaSchemeID) = 'SP'], \"not(contains(normalize-space($VAR/@schemeID), ' ')) and contains('{TSR_CONST_CL_SPIDTYPE}', concat(' ', normalize-space($VAR/@schemeID), ' '))\")",
    "SCH-TSR-34": f"u:for_every(tsr:Key[normalize-space(@metaSchemeID) = 'SP'], \"not(contains(normalize-space($VAR/@schemeID), ' ')) and contains('{TSR_CONST_CL_SPIDTYPE}', concat(' ', normalize-space($VAR/@schemeID), ''))\")",
    "SCH-TSR-40": "u:exists(re:match(normalize-space(tsr:ReportPeriod/tsr:StartDate), '^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}$'))",
    "SCH-TSR-41": "u:exists(re:match(normalize-space(tsr:ReportPeriod/tsr:EndDate), '^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}$'))",
    "SCH-TSR-42": "u:compare_date(tsr:ReportPeriod/tsr:EndDate, '>=', tsr:ReportPeriod/tsr:StartDate)",
}
