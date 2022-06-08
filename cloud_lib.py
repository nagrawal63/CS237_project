import boto3
import io
import os
from google.cloud import storage
from azure.storage.blob import BlockBlobService, PublicAccess
import time

GCP_bucket_name= "my-new-bucket113213"
TMP_FILE_NAME = "tmp"

azure_blob_service_client = None
azure_container_name = "cs237version1"

def create_and_write_tmp_file(fileContent):
    f = open("tmp", "w")
    f.write(fileContent)
    f.close()

def remove_file():
    os.remove(TMP_FILE_NAME)

def get_file_content(filename):
    file_content = None
    with open(filename, "r") as f:
        file_content = f.readlines()
    combined_file_string = ''.join(file_content)
    remove_file()
    print("=========================================")
    print(combined_file_string)
    print("=========================================")
    return combined_file_string

def upload_gcp(dest_file_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_bucket_name)
    blob = bucket.blob(dest_file_path)
    blob.upload_from_filename(TMP_FILE_NAME)

def download_gcp(file_path):
    print("Downloading file from gcp with file_path: " + file_path)
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_bucket_name)

    blob = bucket.blob(file_path)
    blob.download_to_filename(TMP_FILE_NAME)
    return get_file_content(TMP_FILE_NAME)

def delete_gcp(file_path):
    pass

def upload_azure(dest_file_path):
    local_path = os.path.expanduser("./")
    if not os.path.exists(local_path):
        os.makedirs(os.path.expanduser("./"))
    full_path_to_file = os.path.join(local_path, TMP_FILE_NAME)

    azure_blob_service_client.create_blob_from_path(
            azure_container_name, dest_file_path, full_path_to_file)
    
    # Hardcoded sleep to let azure do its thing
    time.sleep(0.5)

def download_azure(file_path):
    # time.sleep(5)
    local_path = os.path.expanduser("./")
    if not os.path.exists(local_path):
        os.makedirs(os.path.expanduser("./"))
    full_path_to_file = os.path.join(local_path, TMP_FILE_NAME)
    print("Downloading file from azure with file_path: " + file_path)
    try:
        azure_blob_service_client.get_blob_to_path(
                azure_container_name, file_path, full_path_to_file)
    except Exception as e:
        print("[Cloud_lib] Could not download file from azure")
        return None

    return get_file_content(TMP_FILE_NAME)

def delete_azure(file_path):
    pass

def upload_aws(dest_file_path):
    print("uploading " + dest_file_path + " to aws")
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename=TMP_FILE_NAME,
        Bucket="cs237version1",
        Key=dest_file_path,
    )

def download_aws(file_path):
    print("Downloading file from aws with file_path: " + file_path)
    s3 = boto3.client("s3")
    s3.download_file(
        Bucket="cs237version1", 
        Key=file_path, 
        Filename=TMP_FILE_NAME
    )
    return get_file_content(TMP_FILE_NAME)

def delete_aws(file_path):
    pass

def upload_file(cloud, file_path, fileContent):
    if azure_blob_service_client == None or azure_container_name == None:
        print("[Cloud_lib] Kindly start the fileserver first")
        return
    
    create_and_write_tmp_file(fileContent)
    if cloud == "aws":
        upload_aws(file_path)
    elif cloud == "azure":
        upload_azure(file_path)
    elif cloud == "gcp":
        upload_gcp(file_path)
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")
    remove_file()

def download_file_partition(cloud, file_path):
    if azure_blob_service_client == None or azure_container_name == None:
        print("[Cloud_lib] Kindly start the fileserver first")
        return
    if cloud == "aws":
        return download_aws(file_path)
    elif cloud == "azure":
        return download_azure(file_path)
    elif cloud == "gcp":
        return download_gcp(file_path)
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")
        return None

def delete_file(cloud, file_path):
    if azure_blob_service_client == None or azure_container_name == None:
        print("[Cloud_lib] Kindly start the fileserver first")
        return
    
    if cloud == "aws":
        delete_aws(file_path)
    elif cloud == "azure":
        delete_azure(file_path)
    elif cloud == "gcp":
        delete_gcp(file_path)
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")