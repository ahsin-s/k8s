import time

import boto3
from celery import Celery

session = boto3.Session()
account_id = session.get_credentials().account_id

broker_url = "sqs://"
app = Celery('tasks', broker=broker_url)
app.conf.broker_transport_options = {
    'region': 'us-east-2',
    'queue_name_prefix': 'failed_eventbridge',
    "predefined_queues": {
        "failed_eventbridgecelery": {
            "url": f"https://sqs.us-east-2.amazonaws.com/{account_id}/failed_eventbridge",
        }
    },
}


@app.task
def wait(s: int, *args, **kwargs):
    print("Task started...")
    time.sleep(s)
    print("Task finished!")
    return "done"
