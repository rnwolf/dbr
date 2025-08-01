# OrganizationCreate

Schema for creating a new organization


## Fields

| Field                    | Type                     | Required                 | Description              |
| ------------------------ | ------------------------ | ------------------------ | ------------------------ |
| `name`                   | *str*                    | :heavy_check_mark:       | Organization name        |
| `description`            | *OptionalNullable[str]*  | :heavy_minus_sign:       | Organization description |
| `contact_email`          | *str*                    | :heavy_check_mark:       | Contact email address    |
| `country`                | *str*                    | :heavy_check_mark:       | ISO country code         |
| `subscription_level`     | *Optional[str]*          | :heavy_minus_sign:       | Subscription level       |