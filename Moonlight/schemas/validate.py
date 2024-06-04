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
    
    @staticmethod
    def min_value(min_value: int) -> Any:
        def validator(value):
            if value:
                if value < min_value:
                    raise ValueError(f'Value must be at greater than {min_value}')
                    
            return value
        
        return validator

    @staticmethod
    def max_value(max_value: int) -> Any:
        def validator(value):
            if value:
                if value > max_value:
                    raise ValueError(f'Value must be at less than {max_value}')
                    
            return value
        
        return validator