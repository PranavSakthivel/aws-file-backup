# Pranav Sakthivel
# Python AWS S3 File Backup Program
# This program will backup all files and folders from a specified directory on the local system,
# to an S3 bucket.
# Usage is detailed in the Word document included.
# Basic usage example: python backup.py "C:\Users\Pranav\Desktop\Backup"


from random import randint
import botocore
import boto3
import os
import sys


def main():
    # If there are more than 2 args, backup.py and the directory, error
    if len(sys.argv) != 2:
        print("Invalid number of arguments passed, exiting program.")
        sys.exit()
    # Attempt to create a bucket with a unique identifier
    bucket_name = "css436pranavsbucket" + str(randint(1000, 9999))
    s3 = boto3.resource("s3")  # Create Boto3 resource
    file_path = sys.argv[1]  # Pull file path from first arg

    # Error Handling:
    if not valid_path(file_path):  # Use method to check if the path provided is valid or exists
        sys.exit()

    if s3.Bucket(bucket_name).creation_date is None:  # Check if bucket exists (should not exist)
        print("Bucket to backup does not exist, creating Bucket:", bucket_name)
        s3.create_bucket(CreateBucketConfiguration={'LocationConstraint': "us-west-2"}, Bucket=bucket_name)
    else:  # Edge case, should not hit
        print("Bucket already exists! Continuing with backup..")

    # Runs method to start uploading directory to S3 bucket
    upload_directory(file_path, s3, bucket_name)


# Method to upload directory provided to an S3 bucket.
def upload_directory(local_directory, s3, bucket_name):
    file_counter = 0
    for path, sub_dirs, files in os.walk(local_directory):  # Use os.walk to traverse through directory
        path = path.replace("\\", "/")  # Replace Windows slashes with universal /
        for file in files:  # For each file, create paths
            local_path = os.path.join(path, file)  # Local file path
            relative_path = os.path.relpath(local_path, local_directory)  # Relative file path to upload to on S3
            relative_path = relative_path.replace("\\", "/")  # Fix relative path slashes as well
            try:  # Check if Object already exists on S3 and can be loaded
                s3.Object(bucket_name, relative_path).load()
            except botocore.exceptions.ClientError as e:  # Catch exception not found, upload file if not found
                if e.response['Error']['Code'] == "404":
                    s3.Bucket(bucket_name).upload_file(local_path, relative_path)
                    file_counter += 1
                    print("Uploading file: ", file,
                          " to s3://" + relative_path)  # Show which file was uploaded from and to where
                else:
                    raise
            else:  # If file already exists
                if (int(s3.Object(bucket_name, relative_path).last_modified.timestamp())) < int(
                        os.path.getmtime(local_path)):  # Compare timestamps to check if the file on local is newer
                    print(file, "is newer on the local machine.")  # Notify user that newer file will be overwriting
                    # the old file
                    s3.Bucket(bucket_name).upload_file(local_path, relative_path)  # Upload file from local to rel path
                    file_counter += 1
                    print("Uploading file: ", file, " to s3://" + relative_path)
                else:
                    print("File", file, "on S3 is newer than the local file or unchanged, skipping..")  # Skip file
                    # if S3 copy is newer or unchanged
    print("Number of files backed up:", file_counter)


# Helper method that uses os.path.isdir to check if the path to the file is valid
def valid_path(path):
    if not os.path.isdir(path):
        print("Invalid directory, exiting program.")
        return False
    else:
        return True


# Call main
main()
