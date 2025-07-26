# System
(*system*)

## Overview

### Available Operations

* [advance_time_unit](#advance_time_unit) - Advance Time Unit
* [get_time](#get_time) - Get Current Time
* [set_time](#set_time) - Set System Time

## advance_time_unit

Advance all schedules one time unit left (Manual/Fast-Forward)

This operation simulates the passage of time, moving all active schedules 
one time slot to the left on the DBR board. This can be triggered manually 
(e.g., "Fast-Forward" button) or automatically by the system.

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.system.advance_time_unit(organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `board_config_id`                                                   | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Optional board config ID to filter schedules                        |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.AdvanceTimeResponse](../../models/advancetimeresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_time

Get the current system time

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.system.get_time()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Dict[str, Any]](../../models/.md)**

### Errors

| Error Type               | Status Code              | Content Type             |
| ------------------------ | ------------------------ | ------------------------ |
| errors.UnauthorizedError | 401, 403                 | application/json         |
| errors.NotFoundError     | 404                      | application/json         |
| errors.BadRequestError   | 400, 422                 | application/json         |
| errors.RateLimitedError  | 429                      | application/json         |
| errors.APIError          | 4XX, 5XX                 | \*/\*                    |

## set_time

Set the system time (for testing purposes)

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.system.set_time(time_iso="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `time_iso`                                                          | *str*                                                               | :heavy_check_mark:                                                  | ISO format datetime to set as system time                           |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Dict[str, Any]](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |