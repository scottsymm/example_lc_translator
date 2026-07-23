"""Generate ISO 20022 tsrv.001 XML from a mapped Letter of Credit."""

from __future__ import annotations

from typing import Optional, cast

from lxml import etree

from lc_translator.mapping import Tsrv001MappedLc
from lc_translator.models import Party

_NS = "urn:iso:std:iso:20022:tech:xsd:tsrv.001.001.01"
_ADDRESS_LINE_LIMIT = 70
_MAX_ADDRESS_LINES = 7


def _q(tag: str) -> str:
    """Return a Clark-notation tag in the tsrv.001 namespace."""
    return f"{{{_NS}}}{tag}"


def _address_lines(text: str) -> list[str]:
    """Break text into address lines that fit the XSD limits."""
    lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        for i in range(0, len(raw_line), _ADDRESS_LINE_LIMIT):
            lines.append(raw_line[i : i + _ADDRESS_LINE_LIMIT])
    return lines[:_MAX_ADDRESS_LINES]


def _add_party(parent: etree._Element, tag: str, party: Optional[Party]) -> None:
    """Add a PartyIdentification43 element to the parent."""
    if party is None:
        return
    party_elem = etree.SubElement(parent, _q(tag))
    nm = etree.SubElement(party_elem, _q("Nm"))
    nm.text = party.name[:140]
    address_lines = _address_lines(party.address)
    if address_lines:
        postal = etree.SubElement(party_elem, _q("PstlAdr"))
        for line in address_lines:
            adr_line = etree.SubElement(postal, _q("AdrLine"))
            adr_line.text = line


class Tsrv001Generator:
    """Build a tsrv.001.001.01 XML document from mapped LC data."""

    def generate(self, mapped: Tsrv001MappedLc) -> str:
        """Return a UTF-8 encoded XML string."""
        root = etree.Element(_q("Document"), nsmap={None: _NS})
        issuance = etree.SubElement(root, _q("UdrtkgIssnc"))
        details = etree.SubElement(issuance, _q("UdrtkgIssncDtls"))

        # Undertaking identification
        id_elem = etree.SubElement(details, _q("Id"))
        id_elem.text = mapped.lc_number[:35]

        name = etree.SubElement(details, _q("Nm"))
        name.text = mapped.undertaking_name

        issuance_type = etree.SubElement(details, _q("IssncTp"))
        issuance_type.text = mapped.issuance_type

        # Parties
        _add_party(details, "Applcnt", mapped.applicant)
        _add_party(details, "Issr", mapped.issuer)
        _add_party(details, "Bnfcry", mapped.beneficiary)

        # Dates
        issue_date = etree.SubElement(details, _q("DtOfIssnc"))
        issue_date.text = mapped.issue_date.isoformat()

        # Amount
        amount = etree.SubElement(etree.SubElement(details, _q("UdrtkgAmt")), _q("Amt"))
        amount.set("Ccy", mapped.currency)
        amount.text = str(mapped.amount)

        # Expiry
        expiry_details = etree.SubElement(details, _q("XpryDtls"))
        expiry_terms = etree.SubElement(expiry_details, _q("XpryTerms"))
        dt_choice = etree.SubElement(expiry_terms, _q("DtTm"))
        dt = etree.SubElement(dt_choice, _q("Dt"))
        dt.text = mapped.expiry_date.isoformat()

        # Governance rules
        governance = etree.SubElement(details, _q("GovncRulesAndLaw"))
        rule_id = etree.SubElement(governance, _q("RuleId"))
        rule_code = etree.SubElement(rule_id, _q("Cd"))
        rule_code.text = mapped.governing_rule

        # Terms and conditions
        terms = etree.SubElement(details, _q("UdrtkgTermsAndConds"))
        txt = etree.SubElement(terms, _q("Txt"))
        txt.text = mapped.terms[:20000]

        return cast(
            str,
            etree.tostring(
                root,
                pretty_print=True,
                xml_declaration=True,
                encoding="UTF-8",
            ).decode("utf-8"),
        )
