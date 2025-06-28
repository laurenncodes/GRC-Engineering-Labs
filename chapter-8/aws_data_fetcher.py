"""aws_data_fetcher.py

This module contains helper functions that **pull raw evidence from AWS**.  It
is used throughout the book to demonstrate how you can programmatically collect
compliance data.  Each function here is *read-only* – no changes are made to
your AWS environment.

Key Concepts for Beginners
--------------------------------------------------------------------
• **boto3** – the official AWS SDK for Python. Think of it as a set of pre-built
  HTTP clients; you don’t need to craft REST requests by hand.
• **Sessions vs. Clients** – a *session* stores credentials; a *client* maps to
  a specific AWS service (Security Hub, Config, CloudTrail, …).
• **Pagination** – most AWS APIs return up to 1,000 records; you often need to
  loop over pages to get the full result set.  These examples handle that for
  you.

All functions return plain Python data structures (lists / dicts) so that later
chapters can transform or export them.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta

def create_aws_session(profile_name=None, region_name='us-east-1'):
    """
    Create an AWS session with optional profile and region.
    
    AWS sessions encapsulate your credentials and configuration,
    allowing you to make API calls to AWS services. This function
    creates a session and tests it to ensure credentials are valid.
    
    Args:
        profile_name: AWS CLI profile name (None for default profile)
        region_name: AWS region to connect to (defaults to us-east-1)
    
    Returns:
        boto3.Session object if successful, None if failed
    """
    try:
        if profile_name:
            session = boto3.Session(profile_name=profile_name, region_name=region_name)
        else:
            session = boto3.Session(region_name=region_name)
        
        # Test the session by calling AWS STS (Security Token Service)
        # This verifies our credentials work without doing anything destructive
        session.client('sts').get_caller_identity()
        return session
    
    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
        return None
    except ClientError as e:
        print(f"Error creating AWS session: {e}")
        return None

def fetch_securityhub_failures(session, severity_labels):
    """
    Returns a list of Security Hub findings with ComplianceStatus=FAILED
    and SeverityLabel matching the specified severity levels.
    """
    client = session.client("securityhub")
    paginator = client.get_paginator("get_findings")
    filters = {
        "ComplianceStatus": [{"Value": "FAILED", "Comparison": "EQUALS"}],
        "SeverityLabel": [
            {"Value": lbl, "Comparison": "EQUALS"} for lbl in severity_labels
        ]
    }
    
    findings = []
    try:
        for page in paginator.paginate(Filters=filters):
            findings.extend(page["Findings"])
    except ClientError as e:
        print(f"Error fetching Security Hub findings: {e}")
        return []
    
    return findings

def fetch_config_noncompliance(session, rule_name):
    """
    Returns a list of evaluation results where ComplianceType=NON_COMPLIANT
    for the specified Config rule.
    """
    client = session.client("config")
    paginator = client.get_paginator("get_compliance_details_by_config_rule")

    results = []
    try:
        for page in paginator.paginate(ConfigRuleName=rule_name):
            for evaluation in page["EvaluationResults"]:
                if evaluation["ComplianceType"] == "NON_COMPLIANT":
                    results.append(evaluation)
    except ClientError as e:
        print(f"Error fetching Config compliance details for rule {rule_name}: {e}")
        return []

    return results

def fetch_cloudtrail_events(session, lookup_attributes,
                            start_time=None, end_time=None):
    """
    Returns a list of CloudTrail events matching lookup_attributes
    within the specified time range.
    """
    client = session.client("cloudtrail")
    paginator = client.get_paginator("lookup_events")

    if end_time is None:
        end_time = datetime.utcnow()
    if start_time is None:
        start_time = end_time - timedelta(days=1)

    events = []
    try:
        for page in paginator.paginate(
            LookupAttributes=lookup_attributes,
            StartTime=start_time,
            EndTime=end_time
        ):
            events.extend(page["Events"])
                
    except ClientError as e:
        print(f"Error fetching CloudTrail events: {e}")
        return []

    return events

if __name__ == '__main__':
    # Example usage: Replace 'default' with your AWS CLI profile if needed
    aws_session = create_aws_session(profile_name='default')

    if aws_session:
        print("Successfully created AWS session.")

        # 1. Fetch HIGH and CRITICAL severity findings from Security Hub
        print("\nFetching high/critical Security Hub findings...")
        high_sev_findings = fetch_securityhub_failures(aws_session, ["HIGH", "CRITICAL"])
        print(f"Found {len(high_sev_findings)} findings.")
        if high_sev_findings:
            print(f"  Example Finding ID: {high_sev_findings[0]['Id']}")

        # 2. Fetch non-compliant resources for a specific Config rule
        print("\nFetching non-compliant resources for 's3-bucket-public-access-prohibited'...")
        s3_violations = fetch_config_noncompliance(aws_session, 's3-bucket-public-access-prohibited')
        print(f"Found {len(s3_violations)} non-compliant S3 buckets.")

        # 3. Fetch recent user creation events from CloudTrail
        print("\nFetching 'CreateUser' events from the last 24 hours...")
        user_creation_events = fetch_cloudtrail_events(aws_session, [{'AttributeKey': 'EventName', 'AttributeValue': 'CreateUser'}])
        print(f"Found {len(user_creation_events)} 'CreateUser' events.")
