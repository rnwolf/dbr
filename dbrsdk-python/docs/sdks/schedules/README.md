# Schedules
(*schedules*)

## Overview

### Available Operations

* [list](#list) - Get Schedules
* [create](#create) - Create Schedule
* [get](#get) - Get Schedule
* [update](#update) - Update Schedule
* [delete](#delete) - Delete Schedule
* [get_board_analytics](#get_board_analytics) - Get Board Analytics

## list

Get all schedules with optional filtering

### Example Usage

<!-- UsageSnippet language="python" operationID="get_schedules_api_v1_schedules_get" method="get" path="/api/v1/schedules" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.list(organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to filter by                                        |
| `board_config_id`                                                   | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Board configuration ID to filter by                                 |
| `status`                                                            | List[*str*]                                                         | :heavy_minus_sign:                                                  | Status to filter by                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[List[models.ScheduleResponse]](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## create

Create a new schedule

### Example Usage

<!-- UsageSnippet language="python" operationID="create_schedule_api_v1_schedules_post" method="post" path="/api/v1/schedules" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.create(organization_id="<id>", board_config_id="<id>", work_item_ids=[
        "<value 1>",
        "<value 2>",
        "<value 3>",
    ], timezone="UTC")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID                                                     |
| `board_config_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Board configuration ID                                              |
| `work_item_ids`                                                     | List[*str*]                                                         | :heavy_check_mark:                                                  | List of work item IDs                                               |
| `timezone`                                                          | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | Timezone for schedule dates                                         |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ScheduleResponse](../../models/scheduleresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get

Get a specific schedule by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="get_schedule_api_v1_schedules__schedule_id__get" method="get" path="/api/v1/schedules/{schedule_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.get(schedule_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `schedule_id`                                                       | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ScheduleResponse](../../models/scheduleresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## update

Update a schedule by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="update_schedule_api_v1_schedules__schedule_id__put" method="put" path="/api/v1/schedules/{schedule_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.update(schedule_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `schedule_id`                                                        | *str*                                                                | :heavy_check_mark:                                                   | N/A                                                                  |
| `organization_id`                                                    | *str*                                                                | :heavy_check_mark:                                                   | Organization ID to scope the request                                 |
| `status`                                                             | *OptionalNullable[str]*                                              | :heavy_minus_sign:                                                   | Schedule status                                                      |
| `work_item_ids`                                                      | List[*str*]                                                          | :heavy_minus_sign:                                                   | Updated work item IDs                                                |
| `time_unit_position`                                                 | *OptionalNullable[int]*                                              | :heavy_minus_sign:                                                   | Time unit position                                                   |
| `released_date`                                                      | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | Released date                                                        |
| `completion_date`                                                    | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | Completion date                                                      |
| `retries`                                                            | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)     | :heavy_minus_sign:                                                   | Configuration to override the default retry behavior of the client.  |

### Response

**[models.ScheduleResponse](../../models/scheduleresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## delete

Delete a schedule by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="delete_schedule_api_v1_schedules__schedule_id__delete" method="delete" path="/api/v1/schedules/{schedule_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    d_client.schedules.delete(schedule_id="<id>", organization_id="<id>")

    # Use the SDK ...

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `schedule_id`                                                       | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_board_analytics

Get analytics for all schedules on a specific board

### Example Usage

<!-- UsageSnippet language="python" operationID="get_board_analytics_api_v1_schedules_board__board_config_id__analytics_get" method="get" path="/api/v1/schedules/board/{board_config_id}/analytics" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.schedules.get_board_analytics(board_config_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `board_config_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.BoardAnalytics](../../models/boardanalytics.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |