import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from colorama import Fore, init
from botocore import UNSIGNED

init(autoreset=True)


def check_cleartext_access(profile, bucket, region):
    try:
        session = boto3.Session(profile_name=profile)
        creds = session.get_credentials().get_frozen_credentials()

        # HTTP (cleartext) endpoint + auth headers
        s3_plain = boto3.client(
            "s3",
            aws_access_key_id=creds.access_key,
            aws_secret_access_key=creds.secret_key,
            aws_session_token=creds.token,
            region_name=region,
            endpoint_url=f"http://s3.{region}.amazonaws.com",
            config=Config(signature_version="s3v4")
        )

        s3_plain.list_objects_v2(Bucket=bucket, MaxKeys=1)
        return True, 200
    except ClientError as e:
        return False, e.response["ResponseMetadata"]["HTTPStatusCode"]
    except Exception:
        return False, "?"


def scan_s3(profile):
    print(f"[S3] Scanning S3 buckets using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    s3 = session.client("s3")
    sts = session.client("sts")
    iam = session.client("iam")
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

        # Get region
        try:
            loc = s3.get_bucket_location(Bucket=name)
            region = loc.get("LocationConstraint") or "us-east-1"
        except Exception:
            pass

        # Read test (auth)
        try:
            s3.list_objects_v2(Bucket=name, MaxKeys=1)
            readable = True
        except Exception:
            pass

        # Write test (simulation)
        try:
            resp = iam.simulate_principal_policy(
                PolicySourceArn=identity_arn,
                ActionNames=["s3:PutObject"],
                ResourceArns=[f"{arn}/*"]
            )
            dec = resp["EvaluationResults"][0]["EvalDecision"]
            writable = True if dec == "allowed" else False
        except Exception:
            writable = None

        # Public test
        try:
            anon_s3.list_objects_v2(Bucket=name, MaxKeys=1)
            public = True
        except ClientError:
            pass

        # Clear-text test
        cleartext, status = check_cleartext_access(profile, name, region)

        # Output
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
        print(f"{ct_color}Clear-Text: {'[YES]' if cleartext else '[NO]'} (HTTP {status})")
        print(f"{Fore.YELLOW}{'=' * 60}")

