# Pranav Sakthivel
# Python AWS S3 File Restore Program
# This program will restore all files and folders from a specified Bucket from AWS S3,
# to a specified directory on the user's computer.
# Usage is detailed in the Word document included.
# Basic usage example: python restore.py "C:\Users\Pranav\Desktop\Restore" backupbucket100

import boto3
import os
import sys


def main():

    if len(sys.argv) != 3:
        print("Invalid number of arguments, exiting program.")
        sys.exit()
    s3 = boto3.resource("s3")  # Create Boto3 resource

    # Get parameters for directory to save files in and the name of the bucket to store files in.
    directory = sys.argv[1]
    bucket_name = sys.argv[2]
    # Verify if the bucket name passed in is valid by checking if a bucket creation date exists.
    if s3.Bucket(bucket_name).creation_date is None:
        print("Bucket", bucket_name, "is either invalid or does not exist, exiting program.")
        sys.exit()
    # Run method to start file restoration
    restore_bucket(s3, directory, bucket_name)


# Helper method to store the files in the user's local drive from S3.
def restore_bucket(s3, local_directory, bucket_name):
    file_counter = 0
    for file in s3.Bucket(bucket_name).objects.all():
        # Fix slashes in paths to work on Windows
        file_path = os.path.join(local_directory, file.key.replace('/', '\\'))
        # Make the directory locally if it does not exist
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        # If the file already exists, make sure we are not overwriting existing files without permission
        if os.path.exists(file_path):
            if (int(s3.Object(bucket_name, file.key).last_modified.timestamp())) > int(
                    os.path.getmtime(file_path)):  # Check if the last modified of the S3 object is before the one of
                # the local file
                print("File", file.key,
                      "already exists but the file on backup is newer, do you want to overwrite? [y/n]: ")
                answer = None
                while answer not in ("y", "n"):
                    answer = input()
                    if answer == "y":
                        print("Downloading and overwriting file", file.key, "to", file_path)
                        s3.Bucket(bucket_name).download_file(file.key, file_path)
                        file_counter += 1
                    elif answer == "n":
                        print("Skipping file")
                    else:
                        print("Please type y or n:")
            else:
                print("File", file.key, "already exists on the local folder. Skipping.")
        else:  # Download file from S3 to local path
            print("Downloading file s3://" + file.key, "to", file_path)
            s3.Bucket(bucket_name).download_file(file.key, file_path)
            file_counter += 1
    if file_counter == 0:
        print("No files were downloaded.")


# Call main()
main()
