# GetSchedulesAPIV1SchedulesGetRequest


## Fields

| Field                               | Type                                | Required                            | Description                         |
| ----------------------------------- | ----------------------------------- | ----------------------------------- | ----------------------------------- |
| `organization_id`                   | *str*                               | :heavy_check_mark:                  | Organization ID to filter by        |
| `board_config_id`                   | *OptionalNullable[str]*             | :heavy_minus_sign:                  | Board configuration ID to filter by |
| `status`                            | List[*str*]                         | :heavy_minus_sign:                  | Status to filter by                 |