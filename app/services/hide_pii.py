from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


def redact_cv(
    cv_text: str,
    analyzer: AnalyzerEngine,
    anonymizer: AnonymizerEngine,
    header_pct=0.25,
):

    lines = cv_text.splitlines(keepends=True)

    header_lines = max(5, int(len(lines) * header_pct))

    header = "".join(lines[:header_lines])
    body = "".join(lines[header_lines:])

    # Strict redaction for the top of the CV
    header_results = analyzer.analyze(
        text=header,
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "URL"],
        language="en",
    )

    # Find the PERSON entity with the highest score in the header
    first_name = "User"
    person_results = [r for r in header_results if r.entity_type == "PERSON"]
    if person_results:
        best_match = max(person_results, key=lambda x: x.score)
        full_name = header[best_match.start : best_match.end].strip()
        first_name = full_name.split()[0] if full_name else "User"

    # Redact only the header because NER sometimes classifies technical skills as PII, which should not be removed from the body of the CV
    safe_header = anonymizer.anonymize(
        text=header, analyzer_results=header_results
    ).text

    return safe_header + "\n" + body, first_name
