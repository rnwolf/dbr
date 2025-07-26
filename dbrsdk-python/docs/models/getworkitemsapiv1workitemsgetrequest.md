# GetWorkItemsAPIV1WorkitemsGetRequest


## Fields

| Field                        | Type                         | Required                     | Description                  |
| ---------------------------- | ---------------------------- | ---------------------------- | ---------------------------- |
| `organization_id`            | *str*                        | :heavy_check_mark:           | Organization ID to filter by |
| `collection_id`              | *OptionalNullable[str]*      | :heavy_minus_sign:           | Collection ID to filter by   |
| `status`                     | List[*str*]                  | :heavy_minus_sign:           | Status to filter by          |
| `priority`                   | *OptionalNullable[str]*      | :heavy_minus_sign:           | Priority to filter by        |
| `sort`                       | *OptionalNullable[str]*      | :heavy_minus_sign:           | Sort field                   |