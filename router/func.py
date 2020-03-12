import os
import json
import logging
import requests

import azure.functions as func

GitHubToken = os.environ["GitHubToken"]

def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    data = event.get_json()

    logging.info(f'EventGrid Data: {json.dumps(data)}')

    if event.event_type == "Microsoft.MachineLearningServices.ModelRegistered":
        model = str(data["modelName"])
        if "seer" in model.lower():

            version = data["modelVersion"]
            ghSha = data["modelTags"]["github_ref"]

            ghUri = "https://api.github.com/repos/cloudscaleml/seer/dispatches"

            headers = {
                "Accept": "application/vnd.github.everest-preview+json",
                "Authorization": f"token {GitHubToken}"
            }

            data = {
                "event_type": "model-registered", 
                "client_payload": { 
                    "model": model,
                    "version": str(version),
                    "service": f"{model}-svc",
                    "compute_target": "sauron",
                    "github_ref": ghSha,
                    "workspace": "hal",
		            "resource_group": "robots"
                }
            }

            logging.info(f'GitHub POST: {json.dumps(data)}')
            response = requests.post(ghUri, headers=headers, json=json.dumps(data))
            logging.info(f'GitHub Response: {response.json()}')



