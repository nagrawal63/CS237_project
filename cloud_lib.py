import boto3
import io
import os
from google.cloud import storage
from azure.storage.blob import BlockBlobService, PublicAccess
import time

GCP_bucket_name= "my-new-bucket113213"
TMP_FILE_NAME = "tmp"

azure_blob_service_client = None
azure_container_name = None

def create_and_write_tmp_file(fileContent):
    f = open("tmp", "w")
    f.write(fileContent)
    f.close()

def remove_file():
    os.remove("tmp")

def upload_gcp(dest_file_path, fileContent):
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_bucket_name)
    blob = bucket.blob(dest_file_path)
    blob.upload_from_filename(TMP_FILE_NAME)

def download_gcp():
    pass

def upload_azure(dest_file_path):
    local_path = os.path.expanduser("./")
    if not os.path.exists(local_path):
        os.makedirs(os.path.expanduser("./"))
    full_path_to_file = os.path.join(local_path, TMP_FILE_NAME)

    azure_blob_service_client.create_blob_from_path(
            azure_container_name, TMP_FILE_NAME, full_path_to_file)
    
    # Hardcoded sleep to let azure do its thing
    time.sleep(0.5)

def download_azure():
    pass

def upload_aws(dest_file_path, fileContent):
    print("uploading " + dest_file_path + " to aws")
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename="tmp",
        Bucket="cs237version1",
        Key=dest_file_path,
    )

def download_aws():
    pass

def upload_file(cloud, file_path, fileContent):
    create_and_write_tmp_file(fileContent)
    if cloud == "aws":
        upload_aws(file_path, fileContent)
    elif cloud == "azure":
        upload_azure(file_path)
    elif cloud == "gcp":
        upload_gcp(file_path, fileContent)
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")
    remove_file()

def download_file(cloud, file_path):
    if cloud == "aws":
        download_aws(file_path)
    elif cloud == "azure":
        download_aws(file_path)
    elif cloud == "gcp":
        download_aws(file_path)
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")