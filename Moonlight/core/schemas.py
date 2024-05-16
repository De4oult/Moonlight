from typing import Any

from Moonlight.core.validate import Validate

class SchemaMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = { key: value for key, value in attrs.items() if not key.startswith('__')}

        for field in fields:
            attrs.pop(field)

        attrs['fields'] = fields

        return super(SchemaMeta, cls).__new__(cls, name, bases, attrs)

class Schema(metaclass = SchemaMeta):
    def __init__(self, **kwargs) -> None:
        self.data: dict[str, Any] = {}

        for field, validators in self.fields.items():
            if not isinstance(validators, tuple):
                raise ValueError('Validators must be provided as a tuple.')
                
            default_value = validators[0] if validators[0] != Validate.empty else None
            
            self.data[field] = kwargs.get(field, default_value)

            for validator in validators[1:]:
                self.data[field] = validator(self.data[field])
    
    def __call__(self) -> dict[str, Any]:
        return self.data