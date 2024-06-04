# Moonlight Database API

__Moonlight Database__ has a built-in __REST API__ to simplify development. This document describes the __API methods__.

Request methods:
```yaml
0. [GET]  /moonlight/docs
1. [POST] /auth
2. [GET]  /moonlight/create
3. [GET]  /moonlight/databases
4. [POST] /moonlight/<database_id>/push
5. [GET]  /moonlight/<database_id>/all
6. [POST] /moonlight/<database_id>/get
7. [POST] /moonlight/<database_id>/update
8. [GET]  /moonlight/<database_id>/delete
9. [GET]  /moonlight/<database_id>/drop
```

## Methods
In the examples, the local URL set in the default Moonlight Database configuration will be used as the URL for requests.

### /moonlight/docs
Returns the API documentation in HTML.

```bash
curl --location 'http://127.0.0.1:3000/moonlight/docs'
```

### /auth
The method for authorization in the database. 

Creates an _authorization key_ that will be valid for __3 hours__. For requests that require authorization, __you need to add Authorization as a Header__.

```bash
curl --location 'http://127.0.0.1:3000/auth' \
     --header 'Content-Type: application/json' \
     --data '{
         "username" : "admin",
         "password" : "admin"
     }'
```

Returns:
```json
"data": {
    "token"   : "703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa",
    "expires" : "<expiration date :str>"
}
```

### /moonlight/create
Creates a database with the name passed in the URL argument __name__.

#### Arguments:
* ___name___ (__str__) - name of database

```bash
curl --location 'http://127.0.0.1:3000/moonlight/create?name=products'
```

<br>

Returns:
```json
{
    "data": {
        "id"      : 18173455252491,
        "message" : "The database has been created successfully"
    }
}
```

### /moonlight/databases
Returns a list of all databases with information about each one.

```bash
curl --location 'http://127.0.0.1:3000/moonlight/databases'
```

<br>

Returns:
```json
{
    "data": {
        "databases": [
            {
                "id"         : 18173455252491,
                "name"       : "products",
                "path"       : "<the path to the database on disk     :str>",
                "logs_path"  : "<the path to the log file on the disk :str>",
                "created_at" : "04-06-2024 11:35:48",
                "author"     : "admin"
            }
        ]
    }
}
```

### /moonlight/<database_id>/push
Creates a record in the database.

#### Body [JSON]:
* ___query___ (__object__) - a record object containing data to be added to the database
    * ___data___

<br>

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/push' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa' \
     --header   'Content-Type: application/json' \
     --data     '{
         "query" : {
             "name"        : "Shortbread cookies with chocolate",
             "count"       : 12,
             "description" : "Delicious shortbread cookies with chocolate chips.",
             "price"       : 1.29,
             "currency"    : "EUR",
             "composition" : ["Butter", "Egg", "Flour", "Baking powder", "Sugar", "Vanilla sugar", "Chocolate"]
         }
     }'
```

<br>

Returns:
```json
{
    "data": {
        "id"      : 14497705931379,
        "message" : "The record was successfully added to the database",
        "address" : "18173455252491:14497705931379"
    }
}
```

### /moonlight/<database_id>/all
Returns all records from the database.

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/all' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa' 
```

<br>

Returns:
```json
{
    "data" : {
        "records" : [
            {
                "id"          : 14497705931379,
                "name"        : "Shortbread cookies with chocolate",
                "count"       : 12,
                "description" : "Delicious shortbread cookies with chocolate chips.",
                "price"       : 1.29,
                "currency"    : "EUR",
                "composition" : [
                    "Butter",
                    "Egg",
                    "Flour",
                    "Baking powder",
                    "Sugar",
                    "Vanilla sugar",
                    "Chocolate"
                ]
            }
        ],
        "message" : "The records were successfully received from the database"
    }
}
```

### /moonlight/<database_id>/get
Returns records for the query contained in the query object

#### Body [JSON]:
* ___query___ (__object__) - a record object containing data to be getted from the database
    * ___data___

<br>

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/get' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa' \
     --header   'Content-Type: application/json' \
     --data     '{
         "query" : {
             "name" : "Shortbread cookies with chocolate"
         }
     }'
```

<br>

Returns:
```json
{
    "data" : {
        "records" : [
            {
                "id"          : 14497705931379,
                "name"        : "Shortbread cookies with chocolate",
                "count"       : 12,
                "description" : "Delicious shortbread cookies with chocolate chips.",
                "price"       : 1.29,
                "currency"    : "EUR",
                "composition" : [
                    "Butter",
                    "Egg",
                    "Flour",
                    "Baking powder",
                    "Sugar",
                    "Vanilla sugar",
                    "Chocolate"
                ]
            }
        ],
        "message" : "The records were successfully received from the database"
    }
}
```

### /moonlight/<database_id>/update
Updates a record in the database by accessing it by ___id___.

#### Body [JSON]:
* ___query___ (__object__) - a record object containing data to be updated in the database
    * ___id___  (__int__)  - record id
    * ___data___

<br>

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/update' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa' \
     --header   'Content-Type: application/json' \
     --data     '{
         "query" : {
             "id"    : 14497705931379, 
             "price" : 1.5
         }
     }'
```

<br>

Returns:
```json
{
    "data" : {
        "id"      : 14497705931379,
        "message" : "The database record has been successfully updated"
    }
}
```

### /moonlight/<database_id>/delete
Deletes a record from the database by accessing it by ___id___.

#### Arguments:
* ___id___ (__int__) - record id

<br>

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/delete?id=14497705931379' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa'
```

<br>

Returns:
```json
{
    "data" : {
        "id"      : 14497705931379,
        "message" : "The record was successfully deleted from the database"
    }
}
```

### /moonlight/<database_id>/drop
Deletes the database

```bash
curl --location 'http://127.0.0.1:3000/moonlight/18173455252491/drop' \
     --header   'Authorization: 703104157117763434aba2d49e395ff87a6377673ef075eec1acd1cdc6c6d9aa'
```

<br>

Returns:
```json
{
    "data" : {
        "id"      : 18173455252491,
        "message" : "The database was successfully deleted"
    }
}
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
