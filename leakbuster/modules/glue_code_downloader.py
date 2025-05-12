import boto3
import os
from urllib.parse import urlparse
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def download_glue_scripts(profile, output_dir="./glue"):
    print(f"[Glue] Downloading Glue job scripts using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    glue = session.client("glue")
    s3 = session.client("s3")

    os.makedirs(output_dir, exist_ok=True)

    try:
        jobs = glue.get_jobs()["Jobs"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list Glue jobs: {e}")
        return

    failures = []

    for job in jobs:
        name = job["Name"]
        script_location = job.get("Command", {}).get("ScriptLocation", "")
        if not script_location.startswith("s3://"):
            print(f"{Fore.YELLOW}Skipping job '{name}' (invalid ScriptLocation)")
            continue

        parsed = urlparse(script_location)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        ext = os.path.splitext(key)[1] or ".py"
        filename = os.path.join(output_dir, f"{name}{ext}")

        print(f"{Fore.CYAN}Processing: {name} -> {filename}")
        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            with open(filename, "wb") as f:
                f.write(obj["Body"].read())
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print(f"{Fore.RED}  Access denied (possibly due to missing kms:Decrypt permission).")
            else:
                print(f"{Fore.RED}  Failed to download {script_location}: {e}")
            failures.append(name)
        except Exception as e:
            print(f"{Fore.RED}  Unexpected error: {e}")
            failures.append(name)

    if failures:
        print(f"\n{Fore.YELLOW}Could not access script for the following jobs:")
        for name in failures:
            print(f"{Fore.YELLOW}  - {name}")

