from pyparsing import Word, alphas, alphanums, Literal, Group, delimitedList, Suppress, Optional, ZeroOrMore, restOfLine

class Moonshard:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.schema_classes = {}
        self.query_classes = {}

    def parse_shard_file(self, content: str):
        identifier = Word(alphas, alphanums + '_')

        schema_keyword = Literal('schema')

        lbrace    = Suppress('{')
        rbrace    = Suppress('}')
        lparen    = Suppress('(')
        rparen    = Suppress(')')
        semicolon = Suppress(';')

        validator = Word(alphas + '_') + Optional(lparen + Word(alphanums) + rparen)
        
        field_def = Group(lparen + delimitedList(validator) + rparen + identifier + semicolon)

        query_keyword = Literal('query')

        arrow = Suppress('->')
        
        # query_param = Group(identifier + arrow + identifier)

        query_condition = Group(identifier + '==' + identifier + semicolon)
        comment = Suppress('?') + restOfLine

        schema_def = schema_keyword + identifier + lbrace + Group(ZeroOrMore(field_def)) + rbrace
        query_def  = query_keyword + identifier + arrow + lparen + Group(delimitedList(identifier)) + rparen + lbrace + Group(ZeroOrMore(query_condition)) + rbrace
        shard_file = ZeroOrMore(schema_def | query_def | comment)

        return shard_file.parseString(content)

    def generate_schema(self, name: str, fields):
        class_def = f'class {name}(Schema):\n'

        for field in fields:
            field_name = field[-1]
            validators = '', ''.join([f'Validate.{value[0]}' + (f'({value[1]})' if len(value) > 1 else '') for value in field[0]])
            class_def += f'    {field_name} = ({validators})\n'

        exec(class_def, globals(), self.schema_classes)
        return self.schema_classes[name]

    def generate_query(self, name, params):
        class_def = f'class {name}(Query):\n'
        init_def = '    def __init__(self, ' + ', '.join(params) + '):\n'
        for param in params:
            init_def += f'        self.{param} = {param}\n'
        class_def += init_def
        exec(class_def, globals(), self.query_classes)
        return self.query_classes[name]

    def compile(self):
        with open(self.file_path, 'r') as file:
            shard_content = file.read()

        parsed_content = self.parse_shard_file(shard_content)

        for item in parsed_content:
            if item[0] == 'schema':
                schema_name = item[1]
                fields = item[2]
                self.generate_schema_class(schema_name, fields)
            elif item[0] == 'query':
                query_name = item[1]
                params = item[2]
                self.generate_query_class(query_name, params)