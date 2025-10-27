from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    
class EmployeeValidator:
    @staticmethod
    def validate_document(document: str) -> ValidationResult:
        errors = []
        if not document or len(document) < 5:
            errors.append("Document ID must be at least 5 characters")
        if not document.isalnum():
            errors.append("Document ID must be alphanumeric")
        return ValidationResult(len(errors) == 0, errors)