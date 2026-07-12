from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CNPJ:
    """CNPJ validado e normalizado (imutável).

    Guarda apenas os 14 dígitos, validando os dígitos verificadores
    conforme o algoritmo oficial da Receita Federal.
    """

    value: str

    def __post_init__(self) -> None:
        digits = "".join(c for c in self.value if c.isdigit())
        if not self._is_valid(digits):
            raise ValueError(f"CNPJ inválido: {self.value!r}")
        object.__setattr__(self, "value", digits)

    @staticmethod
    def _is_valid(digits: str) -> bool:
        """Valida comprimento (14) e os dois dígitos verificadores."""
        if len(digits) != 14:
            return False
        if digits == digits[0] * 14:
            return False
        first = CNPJ._check_digit(digits[:12])
        second = CNPJ._check_digit(digits[:13])
        return digits[12] == str(first) and digits[13] == str(second)

    @staticmethod
    def _check_digit(base: str) -> int:
        """Calcula um dígito verificador do CNPJ para o trecho informado."""
        weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        relevant = weights[-len(base) :]
        total = sum(int(digit) * weight for digit, weight in zip(base, relevant))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    def formatted(self) -> str:
        """Retorna o CNPJ formatado como XX.XXX.XXX/XXXX-XX."""
        d = self.value
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
