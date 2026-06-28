"""
Deploy script — uploads zip to S3, deploys via CloudFormation.
No SAM build needed, no Docker needed.
"""
import boto3, os, sys, time, json

ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(ROOT, "lambda_package.zip")

STACK_NAME = "shopagent"
REGION = os.environ.get("AWS_REGION", "us-east-1")
BUCKET_PREFIX = "shopagent-deploy"
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
STAGE = os.environ.get("STAGE", "prod")


def get_or_create_bucket(s3):
    bucket_name = f"{BUCKET_PREFIX}-{boto3.client('sts').get_caller_identity()['Account']}-{REGION}"
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        print(f"Creating S3 bucket: {bucket_name}")
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION})
    return bucket_name


def upload_zip(s3, bucket):
    key = f"lambda/{int(time.time())}/lambda_package.zip"
    print(f"Uploading {ZIP_PATH} to s3://{bucket}/{key}")
    s3.upload_file(ZIP_PATH, bucket, key)
    return bucket, key


def deploy_stack(cf, bucket, key):
    template_path = os.path.join(ROOT, "template_cf.yaml")

    with open(template_path, 'r') as f:
        template_body = f.read()

    params = [
        {"ParameterKey": "S3Bucket", "ParameterValue": bucket},
        {"ParameterKey": "S3Key", "ParameterValue": key},
        {"ParameterKey": "BedrockModelId", "ParameterValue": MODEL_ID},
        {"ParameterKey": "StageName", "ParameterValue": STAGE},
    ]

    try:
        cf.describe_stacks(StackName=STACK_NAME)
        # stack exists, update
        print(f"Updating stack: {STACK_NAME}")
        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Parameters=params,
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )
        waiter = cf.get_waiter("stack_update_complete")
    except cf.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating stack: {STACK_NAME}")
            cf.create_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Parameters=params,
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )
            waiter = cf.get_waiter("stack_create_complete")
        elif "No updates" in str(e):
            print("No changes to deploy.")
            return
        else:
            raise

    print("Waiting for deploy to complete...")
    waiter.wait(StackName=STACK_NAME)
    print("Deploy complete!")

    # print outputs
    resp = cf.describe_stacks(StackName=STACK_NAME)
    outputs = resp["Stacks"][0].get("Outputs", [])
    for o in outputs:
        print(f"  {o['OutputKey']}: {o['OutputValue']}")


if __name__ == "__main__":
    if not os.path.exists(ZIP_PATH):
        print("No lambda_package.zip found. Run build.py first!")
        sys.exit(1)

    s3 = boto3.client("s3", region_name=REGION)
    cf = boto3.client("cloudformation", region_name=REGION)

    bucket = get_or_create_bucket(s3)
    _, key = upload_zip(s3, bucket)
    deploy_stack(cf, bucket, key)
