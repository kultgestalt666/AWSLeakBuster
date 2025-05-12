import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_api_gateway(profile):
    print(f"[API Gateway] Scanning for public or unprotected APIs using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    apigw = session.client("apigateway")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        apis = apigw.get_rest_apis(limit=500).get("items", [])
    except ClientError as e:
        print(f"{Fore.RED}Failed to list APIs: {e}")
        return

    if not apis:
        print(f"{Fore.GREEN}No REST APIs found.")
        return

    for api in apis:
        api_id = api.get("id")
        name = api.get("name")
        description = api.get("description", "")
        endpoint_url = f"https://{api_id}.execute-api.{region}.amazonaws.com"
        stages = []

        try:
            stages = apigw.get_stages(restApiId=api_id).get("item", [])
        except ClientError:
            pass

        has_public_stage = False
        for stage in stages:
            if not stage.get("methodSettings"):
                has_public_stage = True
            else:
                for _, settings in stage["methodSettings"].items():
                    if not settings.get("authorizationType") or settings.get("authorizationType") == "NONE":
                        has_public_stage = True

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}API:             {name}")
        print(f"{Fore.CYAN}ID:              {api_id}")
        print(f"{Fore.CYAN}ARN:             arn:aws:apigateway:{region}::/restapis/{api_id}")
        print(f"{Fore.CYAN}Endpoint URL:    {endpoint_url}")
        print(f"{Fore.CYAN}Description:     {description}")
        print(f"{Fore.RED if has_public_stage else Fore.GREEN}Public Stage:     {'[YES]' if has_public_stage else '[NO]'}")

        if stages:
            print(f"{Fore.WHITE}Stages:")
            for stage in stages:
                print(f"  - {stage.get('stageName')}")
        else:
            print(f"{Fore.GREEN}No stages found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

