from azure.storage.blob import BlobServiceClient
import json, os
from azure.core.exceptions import ResourceExistsError

conn_str = os.getenv("AZURE_CSV_CONTAINER")
blob_service_client = BlobServiceClient.from_connection_string(str(conn_str))


def log_question(container_name, blob_name, question, time, prompted, flagged):
    """Append {time, question} to JSON line in storage blob"""
    record = {"time": time, "question": question, "prompted": prompted, "flagged": flagged }

    try:
        blob_service_client.create_container(container_name)
    except ResourceExistsError:
        pass

    append_client = blob_service_client.get_blob_client(container_name, blob_name)

    if not append_client.exists():
        append_client.create_append_blob()

    # append just the new line
    line = json.dumps(record, ensure_ascii=False) + "\n"
    append_client.append_block(line.encode("utf-8"))
