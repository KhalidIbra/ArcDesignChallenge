import time
from datetime import datetime, timedelta
from google.cloud import logging

# Defines keywords to search for in the logs
KEYWORDS = ["ERROR", "FAIL"]

# Initializes Google Cloud Logging client
client = logging.Client()

GKE_CLUSTER_NAME = "your-gke-cluster-name"
GKE_NAMESPACE = "your-namespace"
GKE_PROJECT_ID = "your-gke-project-id"
GKE_LOCATION = "your-cluster-region"  # e.g., "us-central1"

# Function to fetch logs from Google Cloud Logging
def fetch_logs():
    # Get the current time and calculate the time 10 minutes ago
    current_time = datetime.utcnow()
    time_10_minutes_ago = current_time - timedelta(minutes=10)

    # Convert the timestamps to RFC3339 format (requirement for by Google Cloud Logging API)
    current_time_rfc3339 = current_time.isoformat("T") + "Z"
    time_10_minutes_ago_rfc3339 = time_10_minutes_ago.isoformat("T") + "Z"

    # Constructs the filter to search logs for the last 10 minutes, for GKE container logs
    filter_str = f"""
        resource.type="k8s_container"
        resource.labels.cluster_name="{GKE_CLUSTER_NAME}"
        resource.labels.namespace_name="{GKE_NAMESPACE}"
        resource.labels.project_id="{GKE_PROJECT_ID}"
        resource.labels.location="{GKE_LOCATION}"
        timestamp >= "{time_10_minutes_ago_rfc3339}" AND
        timestamp <= "{current_time_rfc3339}" AND
        (textPayload:("ERROR") OR textPayload:("FAIL"))
    """

    # Fetch logs from Google Cloud Logging with the specified filter
    for entry in client.list_entries(filter_=filter_str):
        log_message = entry.payload
        log_timestamp = entry.timestamp
        print(f"ALERT: {log_message} at {log_timestamp}")

if __name__ == "__main__":
    print(f"Starting GKE log monitoring for keywords {KEYWORDS} in the cluster '{GKE_CLUSTER_NAME}'...")
    while True:
        # Fetch logs and check for keywords
        fetch_logs()
        # Wait for 60 seconds before checking logs again
        time.sleep(60)
