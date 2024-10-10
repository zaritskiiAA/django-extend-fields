from abc import ABC, abstractmethod
from typing import Any, Callable


class AbstractValidator(ABC):

    @abstractmethod
    def _validate(self, *args, **kwargs):
        pass

    @abstractmethod
    def validate(self, *args, **kwargs):
        pass


class Validator(AbstractValidator):

    def __init__(self, data: Any, validator: Callable[..., None] | None = None) -> None:

        self.data = data

    def validate(self, data: Any, *args, **kwargs) -> Any:
        raise NotImplementedError('Override this method in Validator child.')
    
    def _validate(self, data: Any, *args, **kwargs) -> Any:
        raise NotImplementedError('Override this method in Validator child.')
    

class ValidatorsFabric:

    def generate_validators(
        self, validators: dict[str | Callable[..., None] | object, Any] | None = None,
    ) -> list[Validator] | list:
        
        if validators:
            pass
        else:
            return []
        


