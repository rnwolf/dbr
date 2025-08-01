# Organizations
(*organizations*)

## Overview

### Available Operations

* [get](#get) - Get Organizations
* [create](#create) - Create Organization
* [get_by_id](#get_by_id) - Get Organization
* [update](#update) - Update Organization
* [delete](#delete) - Delete Organization

## get

Get list of organizations (filtered by user permissions)

### Example Usage

<!-- UsageSnippet language="python" operationID="get_organizations_api_v1_organizations__get" method="get" path="/api/v1/organizations/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.organizations.get()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `status`                                                            | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Filter by organization status                                       |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[List[models.OrganizationResponse]](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## create

Create a new organization (Super Admin only)

### Example Usage

<!-- UsageSnippet language="python" operationID="create_organization_api_v1_organizations__post" method="post" path="/api/v1/organizations/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.organizations.create(name="<value>", contact_email="<value>", country="Taiwan", subscription_level="basic")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `name`                                                              | *str*                                                               | :heavy_check_mark:                                                  | Organization name                                                   |
| `contact_email`                                                     | *str*                                                               | :heavy_check_mark:                                                  | Contact email address                                               |
| `country`                                                           | *str*                                                               | :heavy_check_mark:                                                  | ISO country code                                                    |
| `description`                                                       | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Organization description                                            |
| `subscription_level`                                                | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | Subscription level                                                  |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.OrganizationResponse](../../models/organizationresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_by_id

Get a specific organization by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="get_organization_api_v1_organizations__org_id__get" method="get" path="/api/v1/organizations/{org_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.organizations.get_by_id(org_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `org_id`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.OrganizationResponse](../../models/organizationresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## update

Update an organization

### Example Usage

<!-- UsageSnippet language="python" operationID="update_organization_api_v1_organizations__org_id__put" method="put" path="/api/v1/organizations/{org_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.organizations.update(org_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `org_id`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `name`                                                              | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Organization name                                                   |
| `description`                                                       | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Organization description                                            |
| `contact_email`                                                     | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Contact email address                                               |
| `country`                                                           | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | ISO country code                                                    |
| `subscription_level`                                                | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Subscription level                                                  |
| `status`                                                            | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Organization status                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.OrganizationResponse](../../models/organizationresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## delete

Delete an organization (Super Admin only)

### Example Usage

<!-- UsageSnippet language="python" operationID="delete_organization_api_v1_organizations__org_id__delete" method="delete" path="/api/v1/organizations/{org_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.organizations.delete(org_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `org_id`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[Any](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |