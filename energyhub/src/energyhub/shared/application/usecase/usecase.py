"""Interface base de caso de uso da camada de aplicação."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class UseCase(ABC, Generic[Input, Output]):
    """Contrato de um caso de uso: recebe um Input e produz um Output."""

    @abstractmethod
    async def execute(self, input_data: Input) -> Output:
        """Executa o caso de uso."""
        raise NotImplementedError
