# DBR Backend

Run the FastAPI application from within the dbr_mvp/backend directory using the following command:

`uv run uvicorn dbr.main:app --reload`
or on an specific port use
`uv run uvicorn dbr.main:app --reload --port 8002`

## Documentation of the OpenAPI based Swagger UI

http://127.0.0.1:8000/docs
or
http://127.0.0.1:8000/scalar


## DateTime issue with OpenAPI and Pydantic

https://www.speakeasy.com/openapi/frameworks/fastapi

When using Pydantic to define models, a known issue is that the serialization of datetime objects is not timezone-aware. This will cause a mismatch with the OpenAPI format date-time, which requires RFC 3339 date-time strings with timezones included. Consider using
[AwareDatetime](https://docs.pydantic.dev/2.5/api/types/#pydantic.types.AwareDatetime) fields in Pydantic models to enable the appropriate [validation](https://docs.pydantic.dev/latest/errors/validation_errors/#timezone_aware) and ensure your SDK behavior matches the response definition from your server.


## Tools


### SDK generator for OpenAPI services

https://www.speakeasy.com/product/sdk-generation

Turn your OpenAPI spec into production-ready, idiomatic SDKs across multiple languages.

https://github.com/speakeasy-api/speakeasy/releases

`speakeasy quickstart`

`speakeasy lint openapi.yaml`


### Scalar - Improved interactive API documentation

Offline API Client built for working with OpenAPI Schema
https://scalar.com/download


### OpenAPI Linting - Vaccum


`vacuum lint -d 2025-07-23_openapi.json`

https://github.com/daveshanley/vacuum

https://quobix.com/vacuum/

Designed to reliably lint OpenAPI specifications, very, very quickly. Including very large ones. Spectral. can be quite slow when used as an API and does not scale for enterprise applications.

vacuum will tell you what is wrong with your spec, why, where and how to fix it. It will work at scale and is designed as a CLI (with a UI) and a library to be consumed in other applications.


### Security testing frameworks

Explore frameworks like [OWASP ZAP](https://www.zaproxy.org/)  that can verify API security controls.


### Contract testing

Can be done with Pact that formalize the provider-consumer contract but requires test for both publishers and consumers.
Does not make sense in this project. See [PACT vs OpenAPI](https://www.speakeasy.com/blog/pact-vs-openapi) testing considerations.


### Describing Workflows for testing with Arazzo

https://www.openapis.org/arazzo-specification

The Arazzo Specification defines a standard, programming language-agnostic mechanism to express sequences of calls and articulate the dependencies between them to achieve a particular outcome, or set of outcomes, when dealing with API descriptions (such as OpenAPI descriptions).

See [ChatGPT Arazzo](https://chatgpt.com/g/g-673339c216648190a97a5fa3d8258769-arazzo-specification) to get help crafting an API workflow for a given usecase that you can provide. https://www.youtube.com/watch?v=cfh2Y2VKFfY
