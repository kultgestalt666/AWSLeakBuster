import boto3
import os
import zipfile
import shutil
import tempfile
from urllib.request import urlretrieve
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

init(autoreset=True)

def scan_lambda_code(profile, output_dir="lambda"):
    print(f"[Lambda] Downloading and extracting Lambda code using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    client = session.client("lambda")

    os.makedirs(output_dir, exist_ok=True)
    errors = []

    paginator = client.get_paginator("list_functions")
    for page in paginator.paginate():
        for fn in page["Functions"]:
            name = fn["FunctionName"]
            print(f"{Fore.YELLOW}Processing: {name}...")

            try:
                # Get the code download URL
                response = client.get_function(FunctionName=name)
                location = response.get("Code", {}).get("Location")

                if not location:
                    print(f"{Fore.LIGHTBLACK_EX}  No code location found.")
                    errors.append(name)
                    continue

                # Download ZIP to temporary file
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, f"{name}.zip")
                urlretrieve(location, zip_path)

                # Extract ZIP
                extract_path = os.path.join(output_dir, name)
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

                print(f"{Fore.GREEN}  ✓ Extracted to {extract_path}")

                # Cleanup
                shutil.rmtree(temp_dir)

            except ClientError as e:
                code = e.response["Error"]["Code"]
                print(f"{Fore.RED}  Error: {code}")
                errors.append(name)
            except Exception as e:
                print(f"{Fore.RED}  Unexpected error: {str(e)}")
                errors.append(name)

    # Summary
    if errors:
        print(f"\n{Fore.RED}The following functions could not be processed:")
        for fn in errors:
            print(f"  - {fn}")
    else:
        print(f"\n{Fore.GREEN}All functions downloaded successfully.")

