## Moonlight Class Documentation

__Moonlight Class__ - database management class

Has the following set of methods:
```Python
0. async push()
1. async all()
2. async get()
3. async update()
5. async delete()
6. async drop()
7. async contains()
8. async length()
9. async count()
```

To simplify reading, the documentation does not take into account the specifics of working with _async/await_ in _Python_. It is assumed that you are already familiar with them.

### Creating database
You just need to create an instance of the __Moonlight-class__, passing the path to the JSON file as an argument.

For example,
```Python
from MoonlightDB import Moonlight

database: Moonlight = Moonlight('../databases/database.json')
```

#### Arguments
- ___filename___      - path to database .json-file
- ___primary_key___   - primary key name (default: _'id'_) 
- ___show_messages___ - tuple of messages that will be output during operation (default: _('warning', 'error')_)
    * _'success'_
    * _'info'_
    * _'warning'_
    * _'error'_

<br>

### Methods
Method examples will be given using the database variable we set

#### push()
Adds an object with the given fields to the database <br>

#### Arguments:
* ___data_to_push___ (__dict[str, any]__) - the key-value dictionary to be added to the database

Returns ___id___ (__int__).
<br>

```Python
identifier: int = await database.push(
    {
        'name'       : 'Bertram Gilfoyle',
        'job'        : 'Pied Piper Inc.',
        'occupation' : 'Vice President Of Architecture'
    }
)

print(identifier) 
# output >> 22104564398807 
#           ^^^^^^^^^^^^^^
# ID is 14-digit integer
```

#### all()
Get all objects from the database <br>

Returns ___all_objects___ (__list[dict[str, any]]__)
<br>

```Python
data: list[dict[str, any]] = await database.all()

print(data)
# output >> 
# [
#   {
#       'id': 22104564398807, 
#       'name': 'Bertram Gilfoyle', 
#       'job': 'Pied Piper Inc.', 
#       'occupation': 'Vice President Of Architecture'
#   }
# ]
```

#### get()
Get object/s from the database by query <br>

#### Arguments
- ___query___ (__dict[str, any]__) - the key-value dictionary to find in database

Returns ___object/s___ (__list[dict[str, any]]__).
<br>

```Python
data: list[dict[str, any]] = await database.get({
    'job' : 'Pied Piper Inc.'
})

print(data)
# output >> 
# [
#   {
#       'id': 22104564398807, 
#       'name': 'Bertram Gilfoyle', 
#       'job': 'Pied Piper Inc.', 
#       'occupation': 'Vice President Of Architecture'
#   }
# ]
```

#### update()
Update object in the database <br>

#### Arguments
- ___data_to_update___ (__dict[str, any]__) - the key-value dictionary to change in object in database (___primary_key___ in `data_to_update` required!)

Returns ___id___ (__int__).

<br>

```Python
await database.update(
    {
        'id'         : 22104564398807, 
        'occupation' : 'Network engineer'
    }
)
# changed to >> 
# [
#   {
#       'id': 22104564398807, 
#       'name': 'Bertram Gilfoyle', 
#       'job': 'Pied Piper Inc.', 
#       'occupation': 'Network engineer'
#   }
# ]
```

#### delete()
Remove object from the database <br>

#### Arguments
- ___id___ (__14-digit int__) - identifier of element

Returns ___object___ (__dict[str, any]__)
<br>

```Python
await database.delete(22104564398807)

# database file changed to >> 
# {
#   "data": []
# }
#
# will returned >>
#   {
#       'id': 22104564398807, 
#       'name': 'Bertram Gilfoyle', 
#       'job': 'Pied Piper Inc.', 
#       'occupation': 'Network engineer'
#   }
```

#### drop()
Removes database file

```Python
await database.drop()
```

#### contains()
Checks if `key` has a `value` in database <br>

#### Arguments
- ___key___   (__str__)
- ___value___ (__any__)

Returns ___contains___ (__bool__)

```Python
await database.contains('name', 'Bertram Gilfoyle')

# will returned >>
#   True
```

#### length()
Returns count of objects in database <br>

Returns ___length___ (__int__)

```Python
await database.length()

# will returned >>
#   1
```

#### count()
Returns count of objects in database where `key` is `value` <br>

#### Arguments
- ___key___   (__str__)
- ___value___ (__any__)

Returns ___count___ (__int__)

```Python
await database.count('name', 'Bertram Gilfoyle')

# will returned >>
#   1
```

## Schemas
__Schemas__ - method of __organizing__ and __validating__ database __records__ before processing.

### class Validate
Set of validators for __Queries__ and __Schemas__.

__Validators__ act as a set of rules for __Queries__ and __Schemas__ fields. The data transmitted in the field is _checked for correctness_. They __reject the processing__ and __cause an error__ if the _data is incorrect_.

#### Validators:
0. __Validate.empty__ - __placeholder__ if the field has no default data
1. __Validate.required__ - indicates that the field is __required__.
2. __Validate.optional__ - indicates that the field is __optional__.
3. __Validate.min_length(5)__ - specifies the __minimum length__ of __data__ to be __transmitted in the field__
4. __Validate.max_length(10)__ - specifies the __maximum length__ of __data__ to be __transmitted in the field__
5. __Validate.min_value(5)__ - specifies the __minimum value__ of the field
6. __Validate.max_value(10)__ - specifies the __maximum value__ of the field
<br>

### class Schema
Creates a recording scheme to compare the data with before pushing it to the database.

The __default value__ is the first in the __field tuple__ (if there is no such value, specify __Validate.empty__), then the rest of the __validators__.

Example:
```python
from MoonlightDB.schemas.validate import Validate
from MoonlightDB.schemas.schemas  import Schema
from MoonlightDB                  import Moonlight

database: Moonlight = Moonlight('test.json')

class User(Schema):
    username    = (Validate.empty, Validate.required, Validate.min_length(7))
    age         = (Validate.empty, Validate.optional, Validate.min_value(0))
    description = ('Hallo, ich benutze Moonlight', Validate.optional)

user: User = User(
    username = '@de4oult',
    age      = 99
)

await database.push(user)

await database.all()
# ^^^^^^^^^^^^^^^^^
# [
#     {
#         "id"          : 24105894390901,
#         "username"    : "@de4oult"
#         "age"         : 99,
#         "description" : "Hallo, ich benutze Moonlight"
#     }
# ]
```

<br>

### class Query


Example:
```python
from Moonlight.schemas.queries import Query
from Moonlight                 import Moonlight

database = Moonlight('test.json')

class GetByUsername(Query):
    def __init__(self, username: str) -> None:
        self.username = username

class GetByDescription(Query):
    def __init__(self) -> None:
        self.description = 'Hallo, ich benutze Moonlight nicht' # please note, it differs from the default field
 
await database.get(GetByUsername('@de4oult'))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# [
#     {
#         "id"          : 24105894390901,
#         "username"    : "@de4oult"
#         "age"         : 99,
#         "description" : "Hallo, ich benutze Moonlight"
#     }
# ]
await database.get(GetByDescription)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# []
```

<br>

## Author
```
     _      _  _               _ _   
  __| | ___| || |   ___  _   _| | |_ 
 / _` |/ _ \ || |_ / _ \| | | | | __|
| (_| |  __/__   _| (_) | |_| | | |_ 
 \__,_|\___|  |_|  \___/ \__,_|_|\__|
```

## __Thank you a lot!__

<br>

## How to reach me
<a href="https://t.me/de4oult">
    <img src="https://img.shields.io/badge/-Telegram-informational?style=for-the-badge&logo=telegram" alt="Telegram Badge" height="30" />
</a>
<img src="https://img.shields.io/badge/-kayra.dist@gmail.com-informational?style=for-the-badge&logo=gmail" alt="Gmail Badge" height="30" />