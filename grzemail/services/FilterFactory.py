from __future__ import annotations
from datetime import date


def format_date(when: date) -> str:
    return when.strftime("%d-%b-%Y")


class FilterFactory:
    def __init__(self, filters=None) -> None:
        if not filters:
            self._filters = []
        else:
            self._filters = filters
        pass

    def ANSWERED(self) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, "ANSWERED"])

    def BCC(self, who: str) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, f'BCC "{who}"'])

    def BEFORE(self, when: date) -> FilterFactory:
        return FilterFactory(
            filters=[*self._filters, f"BEFORE {format_date(when)}"]
        )

    def BODY(self, string: str) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, f'BODY "{string}"'])

    def CC(self, who: str) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, f'CC "{who}"'])

    def DELETED(self) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, "DELETED"])

    def FROM(self, who: str) -> FilterFactory:
        return FilterFactory(filters=[*self._filters, f'FROM "{who}"'])

    def SINCE(self, when: date) -> FilterFactory:
        return FilterFactory(
            filters=[*self._filters, f"SINCE {format_date(when)}"]
        )

    def make(self) -> str:
        if len(self._filters) == 0:
            return "ALL"
        return " ".join(self._filters)
