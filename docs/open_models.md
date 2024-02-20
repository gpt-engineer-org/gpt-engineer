Using with open/local models
============================

You can integrate `gpt-engineer` with open-source models by leveraging an OpenAI-compatible API.

We provide the minimal and cleanest solution below. It's not the only way to use open/local models but the one we recommend and tested.

Setup
-----

Running the Example
-------------------

On other inference libraries
-------------------

Which open model to use
==================

Your best choice would be:

- CodeLlama
- Mixtral 8x7B

On number of parameters
-------------------

Use the largest model possible that your hardware allows you to run. Sure the responses might be slower but code quality higher.

Using Azure models
==================

You set your Azure OpenAI key:
- `export OPENAI_API_KEY=[your api key]`

Then you call `gpt-engineer` with your service endpoint `--azure https://aoi-resource-name.openai.azure.com` and set your deployment name (which you created in the Azure AI Studio) as the model name (last `gpt-engineer` argument).

Example:
`gpt-engineer --azure https://myairesource.openai.azure.com ./projects/example/ my-gpt4-project-name`
