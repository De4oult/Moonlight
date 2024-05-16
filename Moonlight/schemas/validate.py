from typing import Any

class Validate:
    empty: str = 'placeholder'

    @staticmethod
    def required(value: Any) -> Any:
        if not value:
            raise ValueError('Required field is empty')

        return value
    
    @staticmethod
    def optional(value: Any) -> Any | None:
        return value if value != None else None
    
    @staticmethod
    def min_length(min_length: int) -> Any:
        def validator(value):
            if value:
                if len(value) < min_length:
                    raise ValueError(f'Value must be at least {min_length} characters long')
                    
            return value
        
        return validator

    @staticmethod
    def max_length(max_length: int) -> Any:
        def validator(value):
            if value:
                if len(value) < max_length:
                    raise ValueError(f'Value must be at most {max_length} characters long')
                    
            return value
        
        return validator