import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_snapshots(profile):
    print(f"[Snapshots] Scanning for public EBS and RDS snapshots using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    ec2 = session.client("ec2")
    rds = session.client("rds")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    # EBS Snapshots
    try:
        snapshots = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
        for snap in snapshots:
            snapshot_id = snap["SnapshotId"]
            description = snap.get("Description", "")
            arn = f"arn:aws:ec2:{region}:{account_id}:snapshot/{snapshot_id}"
            try:
                attr = ec2.describe_snapshot_attribute(SnapshotId=snapshot_id, Attribute="createVolumePermission")
                is_public = any(perm.get("Group") == "all" for perm in attr.get("CreateVolumePermissions", []))
            except Exception:
                is_public = False

            print(f"\n{Fore.YELLOW}{'=' * 60}")
            print(f"{Fore.YELLOW}EBS Snapshot ID: {snapshot_id}")
            print(f"{Fore.CYAN}ARN:             {arn}")
            print(f"{Fore.CYAN}Description:     {description}")
            print(f"{Fore.CYAN}Size (GB):       {snap['VolumeSize']}")
            print(f"{Fore.RED if is_public else Fore.GREEN}Public:          {'[YES]' if is_public else '[NO]'}")
            print(f"{Fore.YELLOW}{'=' * 60}")
    except ClientError as e:
        print(f"{Fore.RED}Error fetching EBS snapshots: {e}")

    # RDS Snapshots
    try:
        snapshots = rds.describe_db_snapshots(SnapshotType="manual")["DBSnapshots"]
        for snap in snapshots:
            snapshot_id = snap["DBSnapshotIdentifier"]
            db_instance = snap.get("DBInstanceIdentifier", "")
            arn = snap.get("DBSnapshotArn", f"arn:aws:rds:{region}:{account_id}:snapshot:{snapshot_id}")
            try:
                attrs = rds.describe_db_snapshot_attributes(DBSnapshotIdentifier=snapshot_id)
                is_public = any(attr["AttributeName"] == "restore" and "all" in attr["AttributeValues"]
                                for attr in attrs["DBSnapshotAttributesResult"]["DBSnapshotAttributes"])
            except Exception:
                is_public = False

            print(f"\n{Fore.YELLOW}{'=' * 60}")
            print(f"{Fore.YELLOW}RDS Snapshot ID: {snapshot_id}")
            print(f"{Fore.CYAN}ARN:             {arn}")
            print(f"{Fore.CYAN}DB Instance:     {db_instance}")
            print(f"{Fore.CYAN}Engine:          {snap['Engine']}")
            print(f"{Fore.CYAN}Size (GB):       {snap['AllocatedStorage']}")
            print(f"{Fore.RED if is_public else Fore.GREEN}Public:          {'[YES]' if is_public else '[NO]'}")
            print(f"{Fore.YELLOW}{'=' * 60}")
    except ClientError as e:
        print(f"{Fore.RED}Error fetching RDS snapshots: {e}")

