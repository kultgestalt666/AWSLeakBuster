import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_cognito_identity_pools(profile):
    print(f"[Cognito] Scanning Identity Pools for unauthenticated access using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    cognito = session.client("cognito-identity")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        identity_pools = cognito.list_identity_pools(MaxResults=60)["IdentityPools"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list Cognito Identity Pools: {e}")
        return

    for pool in identity_pools:
        name = pool.get("IdentityPoolName", "N/A")
        pool_id = pool["IdentityPoolId"]
        arn = f"arn:aws:cognito-identity:{region}:{account_id}:identitypool/{pool_id}"

        try:
            details = cognito.describe_identity_pool(IdentityPoolId=pool_id)
            unauth_enabled = details.get("AllowUnauthenticatedIdentities", False)
        except ClientError as e:
            print(f"{Fore.RED}Failed to describe pool '{name}': {e}")
            continue

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Identity Pool:  {name}")
        print(f"{Fore.CYAN}ARN:            {arn}")
        print(f"{Fore.CYAN}Pool ID:        {pool_id}")
        print(f"{Fore.RED if unauth_enabled else Fore.GREEN}Unauthenticated Access: {'[YES]' if unauth_enabled else '[NO]'}")
        print(f"{Fore.YELLOW}{'=' * 60}")

