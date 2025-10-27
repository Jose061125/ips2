from dataclasses import dataclass
from typing import List

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

class DomainValidator:
    @staticmethod
    def validate_document(document: str) -> ValidationResult:
        errors = []
        if not document.isalnum():
            errors.append("Document must be alphanumeric")
        if len(document) < 5:
            errors.append("Document too short")
        return ValidationResult(len(errors) == 0, errors)