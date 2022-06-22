# API Reference

## Getting Started

**Base** URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, http://localhost:5000/, which is set as a proxy in the frontend configuration
**Authentication**: This application require authentication or API keys

## Error Handling
Errors are returned as JSON objects in the following format

```
{
    "success": False,
    "error": 400,
    "message": "bad request"
}
```

The API will return three error types requests fail:

400: Bad Request
404: Resource Not Found
422: Nop Processable

### Endpoints

## GET /codingschools

General:

=======
Returns a list of all codingschools, total number of codingschools and success value
Results are paginated in groups of 3 and include a request argument to choose page number, starting from 1

```
    {
    "list of coding schools": [
        {
        "address": "L8 Barnawa, by Dambo road", 
        "name": "Colab Innovation LTD", 
        "rating": 4, 
        "state": "Kaduna"
        }, 
        {
        "address": "kinkinau gra", 
        "name": "hello", 
        "rating": 2, 
        "state": "kaduna"
        }
    ], 
    "success": true, 
    "total_coding_schools": 2
    }
```

## POST /codingschools

### General:

- [x] Creates a new codingschool using the submitted name, address, state and rating. Returns the id of the created codingschool, success value, total codingschools, and codingschools listed based on the current page number to update the frontend
- [x] `curl http://localhost:5000/codingschools -X POST -H "Content-Type: application/json" -d '{"name": "hello", "address": "kinkinau gra", "state": "kaduna", "rating": 2}'`

```
    {
    "coding_schools": [
        {
        "address": "L8 Barnawa, by Dambo road", 
        "id": 1, 
        "name": "Colab Innovation LTD", 
        "rating": 4, 
        "state": "Kaduna"
        }, 
        {
        "address": "kinkinau gra", 
        "id": 2, 
        "name": "hello", 
        "rating": 2, 
        "state": "kaduna"
        }
    ], 
    "created": 2, 
    "message": "new coding school created", 
    "success": true, 
    "total_coding_schools": 2
    }
```

## PATCH /codingschools/(codingschool_id)

### General:

- [x] if provided, updates the rating of a specified codingschool. Returns the success value and id of the modified codingschool.
`curl http://localhost:5000/codingschools/4 -X PATCH -H "Content-Type: application/json" -d '{"rating": 3}'`

```
{
    "id": 4,
    "success": true
}
```