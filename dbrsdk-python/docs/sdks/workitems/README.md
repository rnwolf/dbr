# WorkItems
(*work_items*)

## Overview

### Available Operations

* [list](#list) - Get Work Items
* [create](#create) - Create Work Item
* [get](#get) - Get Work Item
* [update](#update) - Update Work Item
* [delete](#delete) - Delete Work Item
* [update_task](#update_task) - Update Work Item Task

## list

Get all work items with optional filtering

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to filter by                                        |
| `collection_id`                                                     | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Collection ID to filter by                                          |
| `status`                                                            | List[*str*]                                                         | :heavy_minus_sign:                                                  | Status to filter by                                                 |
| `priority`                                                          | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Priority to filter by                                               |
| `sort`                                                              | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Sort field                                                          |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[List[models.WorkItemResponse]](../../models/.md)**

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

Create a new work item

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.create(organization_id="<id>", title="<value>", estimated_total_hours=5599.86)

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID                                                     |
| `title`                                                             | *str*                                                               | :heavy_check_mark:                                                  | Work item title                                                     |
| `estimated_total_hours`                                             | *float*                                                             | :heavy_check_mark:                                                  | Estimated total hours                                               |
| `collection_id`                                                     | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Collection ID (optional)                                            |
| `description`                                                       | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item description                                               |
| `status`                                                            | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item status                                                    |
| `priority`                                                          | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item priority                                                  |
| `ccr_hours_required`                                                | Dict[str, *float*]                                                  | :heavy_minus_sign:                                                  | CCR hours required                                                  |
| `estimated_sales_price`                                             | *OptionalNullable[float]*                                           | :heavy_minus_sign:                                                  | Estimated sales price                                               |
| `estimated_variable_cost`                                           | *OptionalNullable[float]*                                           | :heavy_minus_sign:                                                  | Estimated variable cost                                             |
| `tasks`                                                             | List[[models.TaskCreate](../../models/taskcreate.md)]               | :heavy_minus_sign:                                                  | Initial tasks                                                       |
| `responsible_user_id`                                               | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Responsible user ID                                                 |
| `url`                                                               | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | External URL                                                        |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.WorkItemResponse](../../models/workitemresponse.md)**

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

Get a specific work item by ID

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.get(work_item_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `work_item_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.WorkItemResponse](../../models/workitemresponse.md)**

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

Update a work item by ID

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.update(work_item_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `work_item_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `collection_id`                                                     | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Collection ID                                                       |
| `title`                                                             | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item title                                                     |
| `description`                                                       | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item description                                               |
| `status`                                                            | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item status                                                    |
| `priority`                                                          | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Work item priority                                                  |
| `estimated_total_hours`                                             | *OptionalNullable[float]*                                           | :heavy_minus_sign:                                                  | Estimated total hours                                               |
| `ccr_hours_required`                                                | Dict[str, *float*]                                                  | :heavy_minus_sign:                                                  | CCR hours required                                                  |
| `estimated_sales_price`                                             | *OptionalNullable[float]*                                           | :heavy_minus_sign:                                                  | Estimated sales price                                               |
| `estimated_variable_cost`                                           | *OptionalNullable[float]*                                           | :heavy_minus_sign:                                                  | Estimated variable cost                                             |
| `tasks`                                                             | List[Dict[str, *Any*]]                                              | :heavy_minus_sign:                                                  | Tasks list                                                          |
| `responsible_user_id`                                               | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Responsible user ID                                                 |
| `url`                                                               | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | External URL                                                        |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.WorkItemResponse](../../models/workitemresponse.md)**

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

Delete a work item by ID

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    d_client.work_items.delete(work_item_id="<id>", organization_id="<id>")

    # Use the SDK ...

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `work_item_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
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

## update_task

Update a specific task within a work item

### Example Usage

```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.update_task(work_item_id="<id>", task_id=744912, organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `work_item_id`                                                      | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `task_id`                                                           | *int*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `title`                                                             | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Task title                                                          |
| `completed`                                                         | *OptionalNullable[bool]*                                            | :heavy_minus_sign:                                                  | Task completion status                                              |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.WorkItemResponse](../../models/workitemresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.BadRequestError     | 400                        | application/json           |
| errors.UnauthorizedError   | 401, 403                   | application/json           |
| errors.NotFoundError       | 404                        | application/json           |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.RateLimitedError    | 429                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |