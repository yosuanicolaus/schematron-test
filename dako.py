import sys
from time import time
from typing import Any

from lxml import etree
from rich.pretty import pprint
from saxonche import PySaxonProcessor

from schematron_lxml_const import (
    SCHEMATRON_CEN_PATH,
    SCHEMATRON_EUSR_PATH,
    SCHEMATRON_NLCIUS_PATH,
    SCHEMATRON_PEPPOL_PATH,
    SCHEMATRON_PINT_AUNZ_PATH,
    SCHEMATRON_PINT_COMMON_PATH,
    SCHEMATRON_TSR_PATH,
    SCHEMATRON_XRECHNUNG_PATH,
    get_file_and_schematron_paths,
)

SCHEMATRON_STYLESHEET_MAP = {
    SCHEMATRON_CEN_PATH: "./validation/saxonche/cen.xsl",
    SCHEMATRON_PEPPOL_PATH: "./validation/saxonche/peppol.xsl",
    SCHEMATRON_NLCIUS_PATH: "./validation/saxonche/nlcius.xsl",
    SCHEMATRON_EUSR_PATH: "./validation/saxonche/eusr.xsl",
    SCHEMATRON_TSR_PATH: "./validation/saxonche/tsr.xsl",
    SCHEMATRON_XRECHNUNG_PATH: "./validation/saxonche/cen.xsl",  # TODO: add xrechnung.xsl if we can find it
    SCHEMATRON_PINT_AUNZ_PATH: "./validation/saxonche/pintau1.xslt",
    SCHEMATRON_PINT_COMMON_PATH: "./validation/saxonche/pintau2.xslt",
}

STYLESHEET_NAME_MAP = {}


def main():
    tt = time()

    source_file, schematrons = get_file_and_schematron_paths(sys.argv[1:])
    stylesheets: list[tuple[str, Any]] = []

    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        for schematron_path in schematrons:
            compiled_sch = xsltproc.compile_stylesheet(stylesheet_file=SCHEMATRON_STYLESHEET_MAP[schematron_path])
            stylesheets.append((schematron_path, compiled_sch))

    with PySaxonProcessor(license=False):
        print("=" * 80)
        for sch_path, sch in stylesheets:
            print("Running", sch_path)
            output = sch.transform_to_string(source_file=source_file)
            svrl = etree.fromstring(output.encode()).getroottree()
            warning = [elem.findtext("{*}text") for elem in svrl.findall('.//{*}failed-assert[@flag="warning"]')]
            fatal = [elem.findtext("{*}text") for elem in svrl.findall('.//{*}failed-assert[@flag="fatal"]')]
            print("Warning:")
            pprint(warning)
            print("Fatal:")
            pprint(fatal)
            print("=" * 80)

    print(time() - tt)


if __name__ == "__main__":
    main()
