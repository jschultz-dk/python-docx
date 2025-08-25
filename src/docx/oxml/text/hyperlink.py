"""Custom element classes related to hyperlinks (CT_Hyperlink)."""

from __future__ import annotations
from typing import TYPE_CHECKING, List

from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml.simpletypes import ST_OnOff, ST_String, XsdString
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.text.run import CT_R
from docx.oxml.xmlchemy import (
    BaseOxmlElement,
    OptionalAttribute,
    ZeroOrMore,
)

if TYPE_CHECKING:
    from docx.oxml.text.pagebreak import CT_LastRenderedPageBreak


class CT_Hyperlink(BaseOxmlElement):
    """`<w:hyperlink>` element, containing the text and address for a hyperlink."""

    r_lst: List[CT_R]

    rId: str | None = OptionalAttribute("r:id", XsdString)  # pyright: ignore[reportAssignmentType]
    anchor: str | None = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "w:anchor", ST_String
    )
    history: bool = OptionalAttribute(  # pyright: ignore[reportAssignmentType]
        "w:history", ST_OnOff, default=True
    )

    r = ZeroOrMore("w:r")

    @property
    def lastRenderedPageBreaks(self) -> List[CT_LastRenderedPageBreak]:
        """All `w:lastRenderedPageBreak` descendants of this hyperlink."""
        return self.xpath("./w:r/w:lastRenderedPageBreak")

    @property
    def text(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """The textual content of this hyperlink.

        `CT_Hyperlink` stores the hyperlink-text as one or more `w:r` children.
        """
        return "".join(r.text for r in self.xpath("w:r"))



from typing import Tuple

def build_hyperlink(part,
                    url: str,
                    text: str | None = None,
                    *,
                    tooltip: str | None = None,
                    color: str = "0000FF",
                    underline: bool = True,
                    anchor: str | None = None) -> Tuple[object, object]:
    """
    Build a w:hyperlink element and its inner w:r run.

    Returns:
        (hyperlink_element, run_element)
    """
    # Localize imports to keep callers light


    hyperlink = OxmlElement('w:hyperlink')

    if anchor:
        # Internal link (bookmark)
        hyperlink.set(qn('w:anchor'), anchor)
        if tooltip:
            hyperlink.set(qn('w:tooltip'), tooltip)
        visible_text = text if text is not None else anchor
    else:
        # External link
        r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
        hyperlink.set(qn('r:id'), r_id)
        if tooltip:
            hyperlink.set(qn('w:tooltip'), tooltip)
        visible_text = text if text is not None else url

    # Create run with basic hyperlink styling
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color.lstrip('#'))
        rPr.append(c)

    # Underline control
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single' if underline else 'none')
    rPr.append(u)

    # Apply Word's built-in Hyperlink style
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), 'Hyperlink')
    rPr.append(rStyle)

    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = visible_text

    r.append(rPr)
    r.append(t)
    hyperlink.append(r)

    return hyperlink, r