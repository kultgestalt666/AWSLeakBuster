import boto3
import requests
import json
from botocore.exceptions import ClientError
from botocore import UNSIGNED
from botocore.config import Config
from colorama import Fore, init

init(autoreset=True)

def scan_s3(profile):
    print(f"[S3] Scanning S3 buckets using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    s3 = session.client("s3")
    sts = session.client("sts")
    iam = session.client("iam")

    # Anonymous S3 client (like --no-sign-request)
    anon_s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

    try:
        identity_arn = sts.get_caller_identity()["Arn"]
        buckets = s3.list_buckets()["Buckets"]
    except ClientError as e:
        print(f"{Fore.RED}Error listing buckets: {e}")
        return

    for bucket in buckets:
        name = bucket["Name"]
        arn = f"arn:aws:s3:::{name}"
        region = "unknown"
        readable = False
        writable = None
        public = False
        cleartext = False
        cleartext_status = "?"

        # Get region
        try:
            loc = s3.get_bucket_location(Bucket=name)
            region = loc.get("LocationConstraint") or "us-east-1"
        except Exception:
            pass

        # Read test (authenticated)
        try:
            s3.list_objects_v2(Bucket=name, MaxKeys=1)
            readable = True
        except Exception:
            pass

        # Write test via simulation
        try:
            response = iam.simulate_principal_policy(
                PolicySourceArn=identity_arn,
                ActionNames=["s3:PutObject"],
                ResourceArns=[f"{arn}/*"]
            )
            decision = response["EvaluationResults"][0]["EvalDecision"]
            if decision == "allowed":
                writable = True
            elif decision in ["explicitDeny", "implicitDeny"]:
                writable = False
        except Exception:
            writable = None

        # Public test (unauthenticated access)
        try:
            anon_s3.list_objects_v2(Bucket=name, MaxKeys=1)
            public = True
        except ClientError:
            pass

        # Clear-text test via HTTP
        try:
            http_url = f"http://{name}.s3.{region}.amazonaws.com/"
            resp = requests.get(http_url, timeout=3, allow_redirects=False)
            cleartext_status = str(resp.status_code)
            if resp.status_code == 200:
                cleartext = True
            else:
                cleartext = False
        except Exception:
            cleartext_status = "?"
            cleartext = False

        # Ausgabe
        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Bucket: {name}")
        print(f"{Fore.CYAN}Region: {region}")
        print(f"{Fore.CYAN}ARN:    {arn}")

        print(f"{Fore.RED if readable else Fore.GREEN}Readable:   {'[YES]' if readable else '[NO]'}")

        if writable is True:
            print(f"{Fore.RED}Writable:   [YES]")
        elif writable is False:
            print(f"{Fore.GREEN}Writable:   [NO]")
        else:
            print(f"{Fore.YELLOW}Writable:   [?]")

        print(f"{Fore.RED if public else Fore.GREEN}Public:     {'[YES]' if public else '[NO]'}")

        ct_color = Fore.RED if cleartext else Fore.GREEN
        print(f"{ct_color}Clear-Text: {'[YES]' if cleartext else '[NO]'} (HTTP {cleartext_status})")

        print(f"{Fore.YELLOW}{'=' * 60}")

