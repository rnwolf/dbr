<!-- Start SDK Example Usage [usage] -->
```python
# Synchronous Example
from dbrsdk import Dbrsdk
import os


with Dbrsdk(
    http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
) as d_client:

    res = d_client.work_items.list(organization_id="<id>")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from dbrsdk import Dbrsdk
import os

async def main():

    async with Dbrsdk(
        http_bearer=os.getenv("DBRSDK_HTTP_BEARER", ""),
    ) as d_client:

        res = await d_client.work_items.list_async(organization_id="<id>")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->