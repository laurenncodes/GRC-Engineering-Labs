# Chapter 9 – Automating Evidence Collection & Reporting

## Table of Contents

| Area | File | Purpose |
|------|------|---------|
| GitLab Integration | `gitlab_to_asff.py` | Convert GitLab SAST/DAST JSON reports to AWS Security Finding Format (ASFF) |
|  | `gitlab-iam-policy.json` | Least-privilege policy to allow the CI job to call `BatchImportFindings` |
|  | `gitlab-ci-example.yml` | Sample GitLab job snippet that runs the converter |
| Weekly Audit Report | `weekly_audit_report.py` | Lambda that produces Excel reports from AWS Audit Manager evidence |
|  | `lambda-scheduler.yml` | SAM/CloudFormation template to deploy & schedule the Lambda |
| Auditor Access | `auditor-iam-policy.json` | Read-only IAM policy for external auditors |
|  | `auditor-iam-role.yml` | CloudFormation template to create an assumable auditor role |


This chapter provides the code and configuration to build an automated evidence collection and reporting system. The examples cover two key GRC automation patterns:

1.  **Integrating Application Security Scans**: Unifying GitLab SAST/DAST findings into AWS Security Hub.
2.  **Automated Audit Reporting**: Generating weekly SOC 2 compliance reports from AWS Audit Manager.

## Files in this Directory

### 1. GitLab to ASFF Converter

-   `gitlab_to_asff.py`: A Python script that transforms GitLab SAST and DAST JSON reports into the AWS Security Finding Format (ASFF). It then imports these findings into AWS Security Hub, creating a single pane of glass for both infrastructure and application security vulnerabilities.
-   `gitlab-iam-policy.json`: The least-privilege IAM policy required for the GitLab CI/CD runner. It grants permission to `securityhub:BatchImportFindings`.
-   `gitlab-ci-example.yml`: An example GitLab CI/CD job configuration. It shows how to execute the Python script as part of a pipeline, using artifacts from previous scan stages and securely passing AWS credentials as CI/CD variables.

### 2. Weekly Audit Report Lambda ("Friday Excel")

-   `weekly_audit_report.py`: A Python Lambda function that automates the generation of SOC 2 compliance reports.
    -   It queries the AWS Audit Manager API to fetch the latest evidence for a given assessment.
    -   It processes the evidence, determines compliance status for each control, and identifies failures.
    -   It generates a multi-sheet Excel report with an executive summary, control status, failed findings, and a full evidence log.
    -   The report is uploaded to a specified S3 bucket.
    -   An email notification with a pre-signed S3 URL is sent to stakeholders (e.g., auditors) via SES.
-   `lambda-scheduler.yml`: An AWS SAM (Serverless Application Model) / CloudFormation template to deploy the reporting solution. It defines:
    -   The Lambda function, its Python runtime, and environment variables.
    -   An IAM role with permissions for Audit Manager, S3, and SES.
    -   An Amazon EventBridge (CloudWatch Events) schedule to trigger the Lambda function automatically every Friday.

### 3. Auditor Access Configuration

-   `auditor-iam-policy.json`: A read-only IAM policy for external auditors. It grants `Get*` and `List*` permissions to AWS Audit Manager while explicitly denying all write actions, ensuring the integrity of the evidence.
-   `auditor-iam-role.yml`: A CloudFormation template to create the `AuditorReadOnlyRole`. It attaches the read-only policy and establishes a trust relationship with the auditor's AWS account, allowing them to assume the role for self-service evidence review.

## How to Use

1.  **GitLab Integration**: Adapt the `gitlab-ci-example.yml` job into your project's `.gitlab-ci.yml`. Configure the required AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.) as protected CI/CD variables in your GitLab project settings.
2.  **Weekly Reporting**: Deploy the `lambda-scheduler.yml` template using the AWS CLI or CloudFormation console. You will need to provide your Audit Manager Assessment ID, an S3 bucket name, and recipient email addresses as parameters.
3.  **Auditor Access**: Deploy the `auditor-iam-role.yml` template, providing the auditor's AWS Account ID as a parameter. Share the resulting Role ARN with the auditor for them to assume.
