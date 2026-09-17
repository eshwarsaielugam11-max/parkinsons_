import json
import re
from typing import List

from pydantic import ValidationError

from ..schemas.report import ReportSchema, RetrievedClinicalEvidence


class ReportValidator:
    """Validate the raw LLM report output against the contract.

    The validator extracts a JSON block from the LLM text (if present), parses it into
    ``ReportSchema`` and then performs additional business‑logic checks:

    * The ``calibrated_probability`` value must match the source prediction exactly
      (within a small rounding tolerance).
    * The mandatory disclaimer must be present and match the required wording.
    * Every ``source_title`` cited in ``retrieved_clinical_evidence`` must be present in
      the list of evidence chunks that were actually retrieved for the session.
    """

    DISCLAIMER_TEXT = (
        "THIS IS AN AI‑BASED SCREENING/DECISION‑SUPPORT OUTPUT, NOT A STANDALONE DIAGNOSIS."
    )

    @staticmethod
    def _extract_json_block(text: str) -> str:
        """Extract a JSON block delimited by ``---REPORT START---`` / ``---REPORT END---``.

        If the markers are not found, the whole string is assumed to be JSON.
        """
        start_marker = "---REPORT START---"
        end_marker = "---REPORT END---"
        if start_marker in text and end_marker in text:
            start = text.index(start_marker) + len(start_marker)
            end = text.index(end_marker, start)
            return text[start:end].strip()
        return text.strip()

    @classmethod
    def _parse_report(cls, text: str) -> ReportSchema:
        json_str = cls._extract_json_block(text)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Report output is not valid JSON: {exc}")
        try:
            return ReportSchema.parse_obj(data)
        except ValidationError as exc:
            raise ValueError(f"Report JSON does not conform to schema: {exc}")

    @classmethod
    def _check_disclaimer(cls, report: ReportSchema) -> None:
        if report.disclaimer.strip() != cls.DISCLAIMER_TEXT:
            raise ValueError("Report disclaimer does not match required wording")

    @classmethod
    def _check_probability(cls, report: ReportSchema, expected: float) -> None:
        # Allow a tolerance of 1e-4 to account for formatting differences.
        if abs(report.calibrated_probability - expected) > 1e-4:
            raise ValueError(
                f"Calibrated probability {report.calibrated_probability} does not match expected {expected}"
            )

    @classmethod
    def _check_citations(
        cls,
        report: ReportSchema,
        retrieved: List[RetrievedClinicalEvidence],
    ) -> None:
        retrieved_titles = {e.source_title for e in retrieved}
        for cited in report.retrieved_clinical_evidence:
            if cited.source_title not in retrieved_titles:
                raise ValueError(
                    f"Cited source '{cited.source_title}' was not part of the retrieved evidence"
                )

    @classmethod
    def validate(
        cls,
        report_text: str,
        expected_calibrated_probability: float,
        retrieved_evidence: List[RetrievedClinicalEvidence],
    ) -> ReportSchema:
        """Run all validation steps.

        Returns the parsed ``ReportSchema`` on success.
        Raises ``ValueError`` with a descriptive message on failure.
        """
        report = cls._parse_report(report_text)
        cls._check_disclaimer(report)
        cls._check_probability(report, expected_calibrated_probability)
        cls._check_citations(report, retrieved_evidence)
        return report

