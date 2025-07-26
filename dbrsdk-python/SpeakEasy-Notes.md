2025-07-25 Support chat

After running 'speakeasy quickstart` you are presented with tips to improve API spec in order to generate better SDK.
Here is Q & A with SpeakEasy support channel.


Q - What am i meant to do with the "Retries should be configured" advice?


A - When you see advice that "Retries should be configured" in the context of Speakeasy, it means we recommend that you should define how your SDK or API client should automatically retry failed requests. This is typically done using the x-speakeasy-retries extension in your OpenAPI document.

https://www.speakeasy.com/docs/customize/runtime/retries


Q - Hi Ash Its not quire clear to me which OpenAPI spec I should add this to. "If you add the ​x-speakeasy-retries​ extension to the root of the OpenAPI document, the SDK Generator will generate a global retry configuration that will be used for all requests made by the SDK."

I assume it must be the overlay?
http://127.0.0.1:8000/openapi.json + C:\Users\rnwol\workspace\dbr\dbrsdk-python\.speakeasy\speakeasy-modifications-overlay.yaml
But then I still see the recommendation that i should add Retry Support.

A - You could add it in overlays or your base spec.

You can add the ​x-speakeasy-retries​ extension either directly to your main OpenAPI spec or via an overlay. If you are using overlays to manage modifications, you should add the extension at the root of your overlay YAML, targeting the root of the OpenAPI document. This ensures the retry configuration is applied globally to all SDK requests.

For the overlay you'd need to make sure you're targeting the root if you choose to go that method. E.G something like:


actions:
  - target: "$"
    description: Add global retries
    update:
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          maxElapsedTime: 3600000
          exponent: 1.5
        statusCodes:
          - 5XX
        retryConnectionErrors: true

Q - The next message I get is about "​Operations Are Missing Error Responses​".
Will this we more changes to the overlay file ?
Customize error handling | Speakeasy
​An error response should be defined for all operations​
Line: 566 etc


A - Hey Rudiger, just hopping in for Ash as they're on EU hours and headed out soon! A lot of these are just suggestions and not hard requirements but what Speakeasy has likely observed for that endpoint is that there's no 4xx or 5xx response codes. You can certainly make these changes in an existing overlay or add a new overlay - we also have a tool for creating an error code overlay that may be helpful 🙂 : https://www.speakeasy.com/docs/speakeasy-reference/cli/suggest/error-types


Q - Can I have multiple overlay files? in the .speakeasy dir? Or does speakeasy modify the target out file with updates?
­`​`speakeasy suggest error-types --schema=C:\Users\rnwol\workspace\dbr\dbrsdk-python\.speakeasy\out.openapi.yaml --out=C:\Users\rnwol\workspace\dbr\tmp\target.yml­``​

A -You can have unlimited overlay files! That would be my suggestion, have a separate file just for the error-types suggestions overlay. Then in the workflow.yaml file, under the overlays section, just add the additional files. There's a great example here: https://github.com/vercel/sdk/blob/main/.speakeasy/workflow.yaml in our customer Vercel's workflow.yaml file for their TypeScript SDK.



Q - Apparently, you support OSS. I have just started and was wondering if I should use this opportunity to use SpeakEasy. I usually work as delivery manager in large organization, but as I am between assignments I am working on OSS tools that the world might find very helpful. See https://github.com/rnwolf/dbr/blob/main/specification.md of what I am building.

https://www.perplexity.ai/search/what-is-drum-buffer-rope-dbr-f-o2c4dtjRS92xRf0FR20V7w


A - Hey Rudiger! Great to meet you :) Awesome to see the project coming together!

Jumping in here to say we’d be happy to support your OSS project with a 1-year license at no cost. That’ll give you full access even if you go above the 50 op limit. The only thing we ask in return is a little marketing love, a LinkedIn shoutout or mention on X would be perfect!

Just a heads up: we’re happy to continue offering support like what you’ve seen here in Slack, but we won't include dedicated support hours as part of the free offering

Let me know if that sounds good!
