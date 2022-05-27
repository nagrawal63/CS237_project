import boto3

# s3 = boto3.resource("s3")

# for bucket in s3.buckets.all():
#     print(bucket.name)

# s3 = boto3.client("s3")

# s3.download_file(
#     Bucket="cs237version1", Key="public_assets/event.ics", Filename="event.ics"
# )

# s3 = boto3.resource('s3')
# s3.Object('your-bucket', 'your-key').delete()


s3.upload_file(
    Filename="data/downloaded_from_s3.csv",
    Bucket="cs237version1",
    Key="new_file.csv",
)