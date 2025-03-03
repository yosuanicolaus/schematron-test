import sys
from time import time

from lxml import etree
from rich.pretty import pprint

from myconst import get_file_and_schematron_paths
from saxonche import PySaxonProcessor

SCHEMATRON_STYLESHEET_MAP = {
    "validation/schematron/CEN-EN16931-UBL.sch": "./validation/saxonche/cen.xsl",
    "validation/schematron/PEPPOL-EN16931-UBL.sch": "./validation/saxonche/peppol.xsl",
    "validation/schematron/SI-UBL-2.0.sch": "./validation/saxonche/peppol.xsl",
    "validation/schematron/peppol-end-user-statistics-reporting-1.1.4.sch": "./validation/saxonche/peppol.xsl",
    "validation/schematron/peppol-transaction-statistics-reporting-1.0.4.sch": "./validation/saxonche/peppol.xsl",
}

STYLESHEET_NAME_MAP = {}


def saxonche():
    tt = time()

    source_file, schematrons = get_file_and_schematron_paths(sys.argv[1:])
    stylesheets: list = []

    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        for schematron_path in schematrons:
            compiled_sch = xsltproc.compile_stylesheet(stylesheet_file=SCHEMATRON_STYLESHEET_MAP[schematron_path])
            stylesheets.append(compiled_sch)
        # peppol_sch = xsltproc.compile_stylesheet(stylesheet_file="./validation/saxonche/peppol.xsl")
        # cen_sch = xsltproc.compile_stylesheet(stylesheet_file="./validation/saxonche/cen.xsl")

    with PySaxonProcessor(license=False):
        for sch in stylesheets:
            print(f"Running {'CEN' if sch == cen_sch else 'PEPPOL'}")
            output = sch.transform_to_string(source_file=source_file)
            svrl = etree.fromstring(output.encode()).getroottree()
            warning = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="warning"]')]
            fatal = [elem.findtext("{*}text") for elem in svrl.findall('//{*}failed-assert[@flag="fatal"]')]
            print("Warning:")
            pprint(warning)
            print("Fatal:")
            pprint(fatal)

    print(time() - tt)


def main():
    saxonche()
