# Evaluations

This folder contains the `evaluator.py` script, which evaluates AI agent's prompts using Azure AI Foundry's built-in evaluators. It assesses key aspects such as:

- **Task Adherence**: Measures how well the agent stays on track to complete a given task.
- **Intent Resolution**: Evaluates the agent's ability to understand and scope the user's intent.
- **Response Completeness**: Checks if the agent's response is complete and accurate.

These evaluations help ensure the quality and safety of agentic workflows. Refer to the [evaluators](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/agent-evaluators) for more information.

## Prerequisites

Before running the script, ensure the following:

1. **Azure AI Foundry Configuration**:
   - The storage account must have SAS enabled.
   - The storage account must have IAM added with the "Storage Blob Data Contributor" role for the user running the script.
   - The connection must be added in the Azure AI Foundry project for the storage account.
   - The storage account must have the IP added for public access.

2. **Environment Variables**:
   Set the following environment variables:
   - `INPUT_AZURE_OPENAI_TARGET_URI`: The target URI for Azure OpenAI.
   - `INPUT_AZURE_OPENAI_SUBSCRIPTION_ID`: The subscription ID for Azure OpenAI.
   - `INPUT_AZURE_OPENAI_RESOURCE_GROUP_NAME`: The resource group name for Azure OpenAI.
   - `INPUT_AZURE_OPENAI_PROJECT_NAME`: The project name for Azure OpenAI.

## How to Run

1. **Navigate to the Folder**:
   ```bash
   cd evaluations
   ```

2. **Run the Script**:
   Execute the script using Python:
   ```bash
   python evaluator.py
   ```

3. **Check the Output**:
   - The raw evaluation results will be saved to `eval-output.json` in the same folder.
   - If configured, the results will also be uploaded to Azure AI Foundry.

## Notes

- Ensure that the Azure AI Foundry project is properly set up and connected to the required resources.
- The script uses the `evaluate` function to perform evaluations such as task adherence, intent resolution, and response completeness.
- The `studio_url` in the output provides a link to the evaluation results in Azure AI Foundry.
