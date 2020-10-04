![pytest](https://github.com/TheWall89/inducoapi/workflows/pytest/badge.svg?branch=master)

# InducOapi

A simple python module to generate OpenAPI Description Documents by supplying request/response bodies.

## Motivation

Sometimes you have a fully functioning HTTP service without OpenAPI documentation.
At some point in time, others may need to use your service.
Writing the documentation by hand is a pain and can feel like an overwhelming job for complex services.
_inducoapi_ helps you generate your OpenAPI Description Documents by taking as input request/response examples plus some
other information.

The generated OpenAPI documentation is validated with [openapi3](https://github.com/Dorthu/openapi3).

_Warning_: This program also generates the `example` fields in OpenAPI schemas by default.
If you have sensible data in your request/response files, disable this feature with `--no-example`.

## Installation

With `pip`:

```shell script
pip install inducoapi
```

With [poetry](https://python-poetry.org/).

```shell script
git clone git@github.com:TheWall89/inducoapi.git
cd inducoapi
poetry install
```

## Usage

### From CLI

`inducoapi` provides its own help. Check it out with:

```shell script
python -m inducoapi -h
```

Let's consider a simple case: you have an HTTP service managing employees.
We want to generate OpenAPI spec for a GET on all the employees, returning a 200 status code:

```shell script
python -m inducoapi GET /employees 200
```

<details><summary>output</summary>

```yaml
openapi: 3.0.0
info:
  title: Generated by InducOapi
  version: v1
paths:
  /employees:
    get:
      responses:
        200:
          description: ''
```

</details>

Now, a GET request with an empty response is not quite useful.
Let's add an argument with a JSON file containing a response example.
Input examples can be found in [examples](examples).

```shell script
python -m inducoapi GET /employees 200 --response examples/employees.json
```

<details><summary>output</summary>

```yaml
openapi: 3.0.0
info:
  title: Generated by InducOapi
  version: v1
paths:
  /employees:
    get:
      responses:
        200:
          description: ''
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    name:
                      type: string
                      example: Dwight Schrute
                    role:
                      type: string
                      example: salesman
```

</details>

Finally, let's try a POST request with both request and response examples.

```shell script
python -m inducoapi POST /employees 201 --request examples/new_employee_req.json --response examples/new_employee_resp.json
```

<details><summary>output</summary>

```yaml
openapi: 3.0.0
info:
  title: Generated by InducOapi
  version: v1
paths:
  /employees:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: Michael Scott
                role:
                  type: string
                  example: manager
      responses:
        201:
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                    example: 4
                  name:
                    type: string
                    example: Michael Scott
                  role:
                    type: string
                    example: manager
```

</details>

If you want to directly write the generated OpenAPI spec in a YAML file, just add `--output openapi.yaml`

### From python

[test_inducoapi.py](tests/test_inducoapi.py) provides usage examples of the module from python.

## TODO list

- [x] Add support for request/response files in YAML
- [x] Add support for `application/yaml` content
- [x] Customize title and version in info
- [x] Package module
- [ ] Generate resource definitions
- [ ] Add support for `headers`
- [ ] Add support for `links`
- [ ] Add support for `format`
