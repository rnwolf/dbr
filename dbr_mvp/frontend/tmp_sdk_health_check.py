
import asyncio
from dbrsdk import Dbrsdk

async def main():
    """Connects to the backend and performs a health check."""
    print("--- DBR SDK Health Check ---")
    backend_url = "http://127.0.0.1:8000"
    print(f"Attempting to connect to backend at: {backend_url}")

    try:
        # Initialize the SDK client
        sdk = Dbrsdk(server_url=backend_url)
        print("SDK client initialized.")

        # Perform the health check
        print("Performing health check...")
        health_response = await sdk.health.get_async()

        if health_response:
            print("Health check successful!")
            # The actual response is raw bytes, so we decode and print it.
            try:
                # The response object from the SDK might not be a standard HTTPX response.
                # Let's inspect it before trying to access attributes.
                print(f"Response Type: {type(health_response)}")
                # Speakeasy-generated SDKs often wrap the response.
                # Let's assume it has a `raw_response` attribute that is an `httpx.Response`.
                if hasattr(health_response, 'raw_response') and hasattr(health_response.raw_response, 'text'):
                     print(f"Response Content: {health_response.raw_response.text}")
                else:
                    # If not, just print the object itself to see what we have.
                    print(f"Full Response Object: {health_response}")

            except Exception as e:
                print(f"Could not parse response details: {e}")
        else:
            print("Health check failed. No response received.")

    except ImportError as e:
        print(f"SDK Import Error: {e}")
        print("   Please ensure the dbrsdk is installed correctly in the environment.")
    except Exception as e:
        print(f"An error occurred during the health check: {e}")

if __name__ == "__main__":
    asyncio.run(main())
