"""The |Footnotes| object and related proxy classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx.blkcntnr import BlockItemContainer
from docx.shared import Parented

if TYPE_CHECKING:
    from docx import types as t
    from docx.oxml.footnote import CT_Footnotes, CT_FtnEnd


class Footnotes(Parented):
    """Proxy object wrapping ``<w:footnotes>`` element."""

    def __init__(self, footnotes: CT_Footnotes, parent: t.ProvidesStoryPart):
        super(Footnotes, self).__init__(parent)
        self._element = self._footnotes = footnotes

    def __getitem__(self, reference_id: int) -> Footnote:
        """A |Footnote| for a specific footnote of reference id, defined with ``w:id`` argument of ``<w:footnoteReference>``. If reference id is invalid raises an |IndexError|"""
        footnote = self._element.get_by_id(reference_id)
        if footnote is None:
            raise IndexError
        return Footnote(footnote, self)

    def __len__(self) -> int:
        return len(self._element)

    def add_footnote(self, footnote_reference_id: int) -> Footnote:
        """Return a newly created |Footnote|, the new footnote will
        be inserted in the correct spot by `footnote_reference_id`.
        The footnotes are kept in order by `footnote_reference_id`."""
        elements = self._element  # for easy access
        # Fast path: empty collection or strictly appending at the end — no shifting needed.
        if len(elements) == 0 or footnote_reference_id > elements[-1].id:
            new_footnote = elements.add_footnote(footnote_reference_id)
            return Footnote(new_footnote, self)

        # Slow path: inserting into the middle or colliding with an existing id.
        # Shift all existing footnotes with id >= target up by 1 to maintain uniqueness.
        # We iterate in reverse to avoid stepping on ids we still need to process.
        new_footnote = None
        # If elements are maintained sorted by id (as typical), we can break once ids drop below the target.
        for index in reversed(range(len(elements))):
            current_id = elements[index].id
            if current_id < footnote_reference_id:
                # Earlier ids are unaffected; we can stop if order-by-id is maintained.
                break
            if current_id == footnote_reference_id and new_footnote is None:
                # Bump the existing one, insert the new before it at the target id.
                elements[index].id = current_id + 1
                new_footnote = elements[index].add_footnote_before(footnote_reference_id)
            else:
                # Bump all others >= target to keep ids unique.
                elements[index].id = current_id + 1

        # If no collision was found (a gap existed), just add a new footnote with the requested id.
        if new_footnote is None:
            new_footnote = elements.add_footnote(footnote_reference_id)

        return Footnote(new_footnote, self)


class Footnote(BlockItemContainer):
    """Proxy object wrapping ``<w:footnote>`` element."""

    def __init__(self, f: CT_FtnEnd, parent: t.ProvidesStoryPart):
        super(Footnote, self).__init__(f, parent)
        self._f = self._element = f

    def __eq__(self, other) -> bool:
        if isinstance(other, Footnote):
            return self._f is other._f
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Footnote):
            return self._f is not other._f
        return True

    @property
    def id(self) -> int:
        return self._f.id
