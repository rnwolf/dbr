# Users
(*users*)

## Overview

### Available Operations

* [get](#get) - Get Users
* [create](#create) - Create User
* [get_by_id](#get_by_id) - Get User
* [update](#update) - Update User
* [delete](#delete) - Delete User

## get

Get list of users (with organization filtering)

### Example Usage

<!-- UsageSnippet language="python" operationID="get_users_api_v1_users__get" method="get" path="/api/v1/users/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.users.get(organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to filter users                                     |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[List[models.UserResponse]](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## create

Create a new user

### Example Usage

<!-- UsageSnippet language="python" operationID="create_user_api_v1_users__post" method="post" path="/api/v1/users/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.users.create(organization_id="<id>", username="Rahsaan.Stamm56", email="Jaquan_Stiedemann@hotmail.com", display_name="Amelia0", password="rc6Gq0W9r6yWRcF", system_role_id="<id>", active_status=True)

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID                                                     |
| `username`                                                          | *str*                                                               | :heavy_check_mark:                                                  | Username                                                            |
| `email`                                                             | *str*                                                               | :heavy_check_mark:                                                  | Email address                                                       |
| `display_name`                                                      | *str*                                                               | :heavy_check_mark:                                                  | Display name                                                        |
| `password`                                                          | *str*                                                               | :heavy_check_mark:                                                  | Password                                                            |
| `system_role_id`                                                    | *str*                                                               | :heavy_check_mark:                                                  | System role ID                                                      |
| `active_status`                                                     | *Optional[bool]*                                                    | :heavy_minus_sign:                                                  | Active status                                                       |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.UserResponse](../../models/userresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_by_id

Get a specific user by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="get_user_api_v1_users__user_id__get" method="get" path="/api/v1/users/{user_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.users.get_by_id(user_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `user_id`                                                           | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.UserResponse](../../models/userresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## update

Update a user

### Example Usage

<!-- UsageSnippet language="python" operationID="update_user_api_v1_users__user_id__put" method="put" path="/api/v1/users/{user_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.users.update(user_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `user_id`                                                           | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `username`                                                          | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Username                                                            |
| `email`                                                             | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Email address                                                       |
| `display_name`                                                      | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Display name                                                        |
| `system_role_id`                                                    | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | System role ID                                                      |
| `active_status`                                                     | *OptionalNullable[bool]*                                            | :heavy_minus_sign:                                                  | Active status                                                       |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.UserResponse](../../models/userresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## delete

Delete a user

### Example Usage

<!-- UsageSnippet language="python" operationID="delete_user_api_v1_users__user_id__delete" method="delete" path="/api/v1/users/{user_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.users.delete(user_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `user_id`                                                           | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Any](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |