# Health
(*health*)

## Overview

### Available Operations

* [get](#get) - Health Check

## get

Health check endpoint for monitoring and frontend connectivity tests

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.health.get()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Any](../../models/.md)**

### Errors

| Error Type               | Status Code              | Content Type             |
| ------------------------ | ------------------------ | ------------------------ |
| errors.UnauthorizedError | 401, 403                 | application/json         |
| errors.NotFoundError     | 404                      | application/json         |
| errors.BadRequestError   | 400, 422                 | application/json         |
| errors.RateLimitedError  | 429                      | application/json         |
| errors.APIError          | 4XX, 5XX                 | \*/\*                    |