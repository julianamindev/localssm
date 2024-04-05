import boto3
import argparse
import subprocess

def get_instance_id(stackname, server, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    if server == "lm":
        value = ["INFORBCLM01LInstance"]
    else:
        value = ["INFORBCDB01Instance"]

    filter = [
        {
            "Name": "tag:aws:cloudformation:stack-name",
            "Values": [stackname]
        },
        {
            "Name": "tag:aws:cloudformation:logical-id",
            "Values": value
        }
    ]

    response = ec2.describe_instances(Filters=filter)

    instance_id = [instance["InstanceId"] for reservation in response["Reservations"] for instance in reservation["Instances"]]
    return instance_id

def start_ssm_session(instance_id, region="us-east-1"):
    # ssm_client = boto3.client("ssm")

    try:
        # subprocess.run(["aws", "ssm", "start-session", "--target", instance_id], check=True)
        subprocess.run(["start", "cmd", "/wait", "/k", "aws", "ssm", "start-session", "--target", instance_id, "--region", region], shell=True, check=True)
        # subprocess.run(["start", "cmd"],shell=True)
    except Exception as e:
        print(f"Error starting SSM session: {e}")


# ==========

region_mapping = {
    "cc1": "ca-central-1"
}


parser = argparse.ArgumentParser(description="Access migops instances via SSM")
parser.add_argument("region", type=str, nargs="?", default="us-east-1", help="AWS region code (default: us-east-1)")

args = parser.parse_args()

stackname = input("migops stackname: ")
server = ""
while server != "lm" and server != "db":
    server = input("lm or db? ").lower()

if args.region in region_mapping:
    args.region = region_mapping[args.region]


instance_id = get_instance_id(stackname, server, region=args.region)[0]

start_ssm_session(instance_id, region=args.region)

