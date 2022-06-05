import boto3
import io
import os

def create_and_write_tmp_file(fileContent):
    f = open("tmp", "w")
    f.write(fileContent)
    f.close()

def remove_file():
    os.remove("tmp")

def upload_gcp():
    pass
def download_gcp():
    pass

def upload_azure():
    pass
def download_azure():
    pass

def upload_aws(file_path, fileContent):
    create_and_write_tmp_file(fileContent)
    print("uploading " + file_path + " to aws")
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename="tmp",
        Bucket="cs237version1",
        Key=file_path,
    )
    remove_file()

def download_aws():
    pass

def upload_file(cloud, file_path, fileContent):
    if cloud == "aws":
        upload_aws(file_path, fileContent)
    elif cloud == "azure":
        upload_azure()
    elif cloud == "gcp":
        upload_gcp()
    else:
        print("[Cloud_lib] Requested to upload to invalid cloud")
