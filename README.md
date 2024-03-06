# Moonlight
<img src="https://i.ibb.co/5k9N9tR/Frame-4.png" alt="Moonlight Logo" height="150" />

<br>

____Moonlight___ is a lightweight JSON-database for Python._

### Installing database library
```bash
pip install Moonlight
```

### Class
Moonlight - database management class

Has the following set of methods:
```Python
0. async push()
1. async all()
2. async get()
3. async update()
5. async delete()
6. async drop()
```

### Creating database
You just need to create an instance of the Moonlight-class, passing the path to the JSON file as an argument.

For example,
```Python
from Moonlight import Moonlight

database: Moonlight = Moonlight('../databases/database.json')
```

#### Arguments
- ___filename___      - path to database .json-file
- ___primary_key___   - primary key name (default: _'id'_) 
- ___show_messages___ - tuple of messages that will be output during operation (default: _('warning', 'error')_)
    * _'success'_
    * _'warning'_
    * _'error'_

<br>

### Methods
<h3>Method examples will be given using the database variable we set. </h3>

### Quick Methods
* ### [0. Moonlight.push](https://github.com/De4oult/Moonlight#push)
* ### [1. Moonlight.all](https://github.com/De4oult/Moonlight#all)
* ### [2. Moonlight.get](https://github.com/De4oult/Moonlight#get)
* ### [3. Moonlight.update](https://github.com/De4oult/Moonlight#update)
* ### [5. Moonlight.delete](https://github.com/De4oult/Moonlight#delete)
* ### [6. Moonlight.drop](https://github.com/De4oult/Moonlight#drop)

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
Removes all database data

<br>

```Python
await database.drop()

# database-file writes >>
# {
#   "data": []
# }
```

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