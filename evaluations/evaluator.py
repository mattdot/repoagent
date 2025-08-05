import os
import json
from pathlib import Path
from azure.ai.evaluation import TaskAdherenceEvaluator, IntentResolutionEvaluator, ResponseCompletenessEvaluator, AzureOpenAIModelConfiguration
from pprint import pprint
from azure.ai.projects import AIProjectClient 
from azure.identity import DefaultAzureCredential
from src.openai_utils import parse_azure_openai_uri
from src.utils import get_env_var

# Evaluate on a dataset and log results to Azure AI Foundry
from azure.ai.evaluation import evaluate

file_name = "eval.jsonl"
current_dir = Path(__file__).parent
eval_output_path = current_dir / f"eval-output.json"

endpoint, deployment_name, api_version = parse_azure_openai_uri(get_env_var("INPUT_AZURE_OPENAI_TARGET_URI"))

model_config = {
        "azure_deployment": deployment_name,
        "azure_endpoint": endpoint,
        "api_version": api_version,
    }
azure_ai_project_details = {
        "subscription_id": get_env_var("INPUT_AZURE_OPENAI_SUBSCRIPTION_ID"),
        "resource_group_name": get_env_var("INPUT_AZURE_OPENAI_RESOURCE_GROUP_NAME"),
        "project_name": get_env_var("INPUT_AZURE_OPENAI_PROJECT_NAME"),
        "project_endpoint": f"{endpoint}/api/projects/{get_env_var('INPUT_AZURE_OPENAI_PROJECT_NAME')}"
    }

# A few things for this to work for storage error
# 1. The Storage should have SAS Enabled: Storage Account > settings > Configuration > Allow storage account key > Enabled
# 2. The Storage should have IAM added as "Storage Blob Data Contributor" role for the user running this code.(User, Managed Identities: AI Foundry, ML Workspace, etc.)
# 3. The Connection should be added in the Azure AI Foundry project for the storage account. AI Foundary > Manaement Center > Connected resource > new connection > Storage account > Account Key type
# 4. Storage account should have IP added : Storgae account >Security + networking > Networking > Public access > Manage > add ur IP

results = evaluate(
        evaluation_name="evaluation-repoagent",
        data=file_name,
        evaluators={   
            "task_adherence": TaskAdherenceEvaluator(model_config=model_config), # Is the Agent Answering the Right Question?
            "intent_resolution": IntentResolutionEvaluator(model_config=model_config),  # Did the Agent Understand the User’s Goal?
            "response_completeness": ResponseCompletenessEvaluator(model_config=model_config), # Is the Agent's response complete and accurate?
        },
        output_path=eval_output_path, # raw evaluation results
        azure_ai_project=azure_ai_project_details, # if you want results uploaded to AI Foundry
    )
# pprint(results)
pprint(f'AI Foundary URL: {results.get("studio_url")}')