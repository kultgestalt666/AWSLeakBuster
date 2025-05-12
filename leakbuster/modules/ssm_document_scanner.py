import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_ssm_documents(profile):
    print(f"[SSM Documents] Scanning for user-created SSM documents using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    ssm = session.client("ssm")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        documents = ssm.list_documents(Filters=[{"Key": "Owner", "Values": ["Self"]}])["DocumentIdentifiers"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list SSM documents: {e}")
        return

    for doc in documents:
        name = doc["Name"]
        doc_type = doc.get("DocumentType", "Unknown")
        arn = f"arn:aws:ssm:{region}:{account_id}:document/{name}"

        try:
            content_response = ssm.get_document(Name=name, DocumentVersion="$LATEST")
            content = content_response.get("Content", "")
        except ClientError as e:
            print(f"{Fore.RED}  Failed to fetch content for document '{name}': {e}")
            continue

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}SSM Document:  {name}")
        print(f"{Fore.CYAN}Type:          {doc_type}")
        print(f"{Fore.CYAN}ARN:           {arn}")

        if content:
            print(f"{Fore.WHITE}Content Preview:")
            for line in content.splitlines():
                print("  " + line.strip())
        else:
            print(f"{Fore.GREEN}No content found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

