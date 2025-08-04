# Collections
(*collections*)

## Overview

### Available Operations

* [get_all](#get_all) - Get Collections
* [create](#create) - Create Collection
* [get_by_id](#get_by_id) - Get Collection
* [update](#update) - Update Collection
* [delete](#delete) - Delete Collection

## get_all

Get all collections for an organization

### Example Usage

<!-- UsageSnippet language="python" operationID="get_collections_api_v1_collections__get" method="get" path="/api/v1/collections/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.collections.get_all(organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to filter by                                        |
| `status`                                                            | *OptionalNullable[str]*                                             | :heavy_minus_sign:                                                  | Filter by collection status                                         |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[List[models.CollectionResponse]](../../models/.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## create

Create a new collection

### Example Usage

<!-- UsageSnippet language="python" operationID="create_collection_api_v1_collections__post" method="post" path="/api/v1/collections/" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.collections.create(organization_id="<id>", name="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                     | Type                                                                          | Required                                                                      | Description                                                                   |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `organization_id`                                                             | *str*                                                                         | :heavy_check_mark:                                                            | Organization ID                                                               |
| `name`                                                                        | *str*                                                                         | :heavy_check_mark:                                                            | Collection name                                                               |
| `description`                                                                 | *OptionalNullable[str]*                                                       | :heavy_minus_sign:                                                            | Collection description                                                        |
| `status`                                                                      | [OptionalNullable[models.CollectionStatus]](../../models/collectionstatus.md) | :heavy_minus_sign:                                                            | Collection status                                                             |
| `estimated_sales_price`                                                       | *OptionalNullable[float]*                                                     | :heavy_minus_sign:                                                            | Estimated sales price                                                         |
| `estimated_variable_cost`                                                     | *OptionalNullable[float]*                                                     | :heavy_minus_sign:                                                            | Estimated variable cost                                                       |
| `retries`                                                                     | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)              | :heavy_minus_sign:                                                            | Configuration to override the default retry behavior of the client.           |

### Response

**[models.CollectionResponse](../../models/collectionresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## get_by_id

Get a specific collection by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="get_collection_api_v1_collections__collection_id__get" method="get" path="/api/v1/collections/{collection_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.collections.get_by_id(collection_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `collection_id`                                                     | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.CollectionResponse](../../models/collectionresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## update

Update a collection by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="update_collection_api_v1_collections__collection_id__put" method="put" path="/api/v1/collections/{collection_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.collections.update(collection_id="<id>", organization_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                     | Type                                                                          | Required                                                                      | Description                                                                   |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `collection_id`                                                               | *str*                                                                         | :heavy_check_mark:                                                            | N/A                                                                           |
| `organization_id`                                                             | *str*                                                                         | :heavy_check_mark:                                                            | Organization ID to scope the request                                          |
| `name`                                                                        | *OptionalNullable[str]*                                                       | :heavy_minus_sign:                                                            | Collection name                                                               |
| `description`                                                                 | *OptionalNullable[str]*                                                       | :heavy_minus_sign:                                                            | Collection description                                                        |
| `status`                                                                      | [OptionalNullable[models.CollectionStatus]](../../models/collectionstatus.md) | :heavy_minus_sign:                                                            | Collection status                                                             |
| `estimated_sales_price`                                                       | *OptionalNullable[float]*                                                     | :heavy_minus_sign:                                                            | Estimated sales price                                                         |
| `estimated_variable_cost`                                                     | *OptionalNullable[float]*                                                     | :heavy_minus_sign:                                                            | Estimated variable cost                                                       |
| `retries`                                                                     | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)              | :heavy_minus_sign:                                                            | Configuration to override the default retry behavior of the client.           |

### Response

**[models.CollectionResponse](../../models/collectionresponse.md)**

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |

## delete

Delete a collection by ID

### Example Usage

<!-- UsageSnippet language="python" operationID="delete_collection_api_v1_collections__collection_id__delete" method="delete" path="/api/v1/collections/{collection_id}" -->
```python
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    d_client.collections.delete(collection_id="<id>", organization_id="<id>")

    # Use the SDK ...

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `collection_id`                                                     | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `organization_id`                                                   | *str*                                                               | :heavy_check_mark:                                                  | Organization ID to scope the request                                |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Errors

| Error Type                 | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| errors.HTTPValidationError | 422                        | application/json           |
| errors.APIError            | 4XX, 5XX                   | \*/\*                      |