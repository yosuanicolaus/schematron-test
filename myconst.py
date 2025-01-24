from typing import TypedDict


SCHEMATRON_CEN_PATH = "validation/schematron/CEN-EN16931-UBL.sch"
SCHEMATRON_PEPPOL_PATH = "validation/schematron/PEPPOL-EN16931-UBL.sch"
SCHEMATRON_NLCIUS_PATH = "validation/schematron/SI-UBL-2.0.sch"
SCHEMATRON_EUSR_PATH = "validation/schematron/peppol-end-user-statistics-reporting-1.1.4.sch"
SCHEMATRON_TSR_PATH = "validation/schematron/peppol-transaction-statistics-reporting-1.0.4.sch"
TEST_INVOICE_PATH = "test_files/invoice.xml"
TEST_INVOICE100_PATH = "test_files/invoice100.xml"
TEST_NLCIUS_PATH = "test_files/nlcius.xml"
TEST_EUSR_PATH = "test_files/eusr.xml"
TEST_TSR_PATH = "test_files/tsr.xml"


class TestMapValue(TypedDict):
    schematron_paths: tuple[str, ...]
    test_file_path: str


TEST_MAP: dict[str, TestMapValue] = {
    "peppol": {
        "schematron_paths": (SCHEMATRON_CEN_PATH, SCHEMATRON_PEPPOL_PATH),
        "test_file_path": TEST_INVOICE_PATH,
    },
    "peppol100": {
        "schematron_paths": (SCHEMATRON_CEN_PATH, SCHEMATRON_PEPPOL_PATH),
        "test_file_path": TEST_INVOICE100_PATH,
    },
    "nlcius": {
        "schematron_paths": (SCHEMATRON_CEN_PATH, SCHEMATRON_NLCIUS_PATH),
        "test_file_path": TEST_NLCIUS_PATH,
    },
    "eusr": {
        "schematron_paths": (SCHEMATRON_EUSR_PATH,),
        "test_file_path": TEST_EUSR_PATH,
    },
    "tsr": {
        "schematron_paths": (SCHEMATRON_TSR_PATH,),
        "test_file_path": TEST_TSR_PATH,
    },
}

