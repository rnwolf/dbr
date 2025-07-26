# WorkItemUpdate


## Fields

| Field                     | Type                      | Required                  | Description               |
| ------------------------- | ------------------------- | ------------------------- | ------------------------- |
| `collection_id`           | *OptionalNullable[str]*   | :heavy_minus_sign:        | Collection ID             |
| `title`                   | *OptionalNullable[str]*   | :heavy_minus_sign:        | Work item title           |
| `description`             | *OptionalNullable[str]*   | :heavy_minus_sign:        | Work item description     |
| `status`                  | *OptionalNullable[str]*   | :heavy_minus_sign:        | Work item status          |
| `priority`                | *OptionalNullable[str]*   | :heavy_minus_sign:        | Work item priority        |
| `estimated_total_hours`   | *OptionalNullable[float]* | :heavy_minus_sign:        | Estimated total hours     |
| `ccr_hours_required`      | Dict[str, *float*]        | :heavy_minus_sign:        | CCR hours required        |
| `estimated_sales_price`   | *OptionalNullable[float]* | :heavy_minus_sign:        | Estimated sales price     |
| `estimated_variable_cost` | *OptionalNullable[float]* | :heavy_minus_sign:        | Estimated variable cost   |
| `tasks`                   | List[Dict[str, *Any*]]    | :heavy_minus_sign:        | Tasks list                |
| `responsible_user_id`     | *OptionalNullable[str]*   | :heavy_minus_sign:        | Responsible user ID       |
| `url`                     | *OptionalNullable[str]*   | :heavy_minus_sign:        | External URL              |