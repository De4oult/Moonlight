## Moonlight Database CLI Documentation

__Moonlight Database CLI__ - command-line interface for Moonlight database that allows you to edit users, manage databases, and view them

CLI methods:
```bash
0. moonlight configure
1. moonlight locale
2. moonlight create-user
3. moonlight create-key
4. moonlight delete-user
5. moonlight create-database
6. moonlight databases
7. moonlight database
8. moonlight delete-database
9. moonlight serve
```

### Moonfile
__Moonfile__ - configuration file that allows automated configuration of the __Moonlight Database__.

Commands:
* PURE - resets the __application configuration__ to the default configuration.
    - __PURE__

* APP - sets the __address__ and __port__ for accessing the database.
    - __APP \<host>:\<port>__
    - __APP 192.168.0.1__
    - __APP 192.168.0.1:5000__

* LOG - specifies which log messages should be displayed in the console. Everything is saved to a log file. (Logs: __info__, __success__, __warning__, __error__) 
    - __LOG \<loggers separated by ','>__
    - __LOG info__
    - __LOG warning, error__
    - __LOG success, warning, error__

* CREATE_USER - creates a user with an __access level__, __username__ and __password__.
    - __CREATE_USER \<access level> \<username> \<password>__
    - __CREATE_USER administrator admin admin__
* DATABASE - creates a database with a __name__ and __author__ (previously created by the user).
    - __DATABASE \<name> @\<username>__
    - __DATABASE default__
    - __DATABASE my_todos @admin__
* IGNORE - causes __Moonfile__ to be __ignored__. The __preset configuration__ will be used.
    - __IGNORE__
* ? - comment
    - __? I hope everything is clear__

#### Access levels:
* __viewer__ - can __read__ records from databases
* __editor__ - can __read__, __push__, __update__ and __delete__ records
* __administrator__ - can __create__ and __manage__ databases, __fully manage__ their records

Example:
```
PURE

APP 127.0.0.1:3000
? do not change the port!!!

LOG info, success, warning, error

CREATE_USER administrator admin admin
```

## CLI Methods
Usage: `moonlight <method name>`

### configure
Calls the __configuration manager__ if the directory contains __Moonfile__, suggests using it for __configuration__.
<br>

### locale
Changes the interface __language__.
<br>

#### Allowed now:
- English
<br>

### create-user
Calls the manager to create user with __username__, __password__ and __access level__.
<br>

### create-key (need auth)
Creates and returns __API key__ for the logged in __user__.
<br>

### delete-user
Deletes the user selected from the list.
<br>

### create-database (need auth)
Creates database with __name__.
<br>

### databases
Displays __table__ of all __existing databases__.
<br>

### database (need auth)
Displays __table__ visualizing the __records__ of __database__ selected from the list.
<br>

### delete-database (need auth)
Deletes __database__ selected from the list.
<br>

### serve
Launches the __API server__.
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