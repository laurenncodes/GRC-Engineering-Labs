9.2  Turning Controls Into Cloud Signals

A guided enablement plan—and why each AWS “switch” exists

⸻

9.2.1  Why Amazon Built These Standards in the First Place

Before we flip any toggles, it helps to know why they exist and how auditors interpret them.

AWS Feature	What it is	Why Amazon created it	How auditors view it
AWS Security Hub – Standards tab	A catalogue of ready-made security controls, each expressed in the Amazon Security Finding Format (ASFF).	To give every customer an opinionated baseline—no need to invent your own S3-encryption check or IAM-MFA rule.	“Independent” automated proof that a control runs continuously, backed by AWS-signed log data.
Foundational Security Best Practices (FSBP)	Amazon-curated controls that apply to every AWS account (S3 encryption, KMS rotation, root-user lock-down, GuardDuty enabled, etc.).	Customers begged for a single superset that maps to CIS, NIST, and ISO without forcing them to compare overlapping frameworks.	Evidence that your cloud matches what AWS itself calls foundational. Hard for auditors to argue with Amazon’s own benchmark.
CIS AWS Foundations Benchmark	A community standard (Center for Internet Security) co-written by AWS, Google, Microsoft & the open-source community.	To provide a vendor-neutral baseline; many regulators (NY DFS, FFIEC) explicitly reference CIS.	A known good “north-star.” If you comply with CIS, you satisfy large chunks of SOC 2, ISO 27001, PCI, etc.
AWS Config Conformance Pack	A CloudFormation bundle that deploys 50-plus managed Config rules in one shot.	To turn the advice of CIS or FSBP into always-on drift detection—Config stores the time-series evidence.	Continuous, timestamped resource states (pass/fail) that map cleanly to SOC 2 “control operating effectiveness.”

Key point
Security Hub tells you when a control fails. AWS Config proves how long it stayed failed (or stayed compliant). Together they give auditors both the snapshot and the history.

⸻

9.2.2  Choosing—and Tuning—the Baselines
	1.	Enable, then prune
	•	Security Hub FSBP & CIS each ship with >200 controls. Turning everything on without triage creates alert fatigue, and your SecOps partners will shut the project down.
	•	Strategy:
	1.	Enable both standards organisation-wide in a staging OU.
	2.	Run for two weeks.
	3.	Mark every finding either Legitimate Gap or Business-Accepted Risk.
	4.	Disable controls that are permanently “N/A” (for example, EKS checks if you do not run Kubernetes).
	2.	Use Config packs only for the rules you plan to enforce
	•	Managed rules cost US $0.001 per evaluation; 70 rules every 24 h across 30 accounts adds up.
	•	Deploy CIS-1.4 and Operational Best Practices for KMS only in production & security accounts. Keep dev accounts lighter to save cost and reduce noise.
	3.	Document every disabled control in Audit Manager
	•	Auditors will ask, “Why is ELB.5 disabled?”—have a one-liner ready:
“Company does not use classic ELBs; all load balancers are ALB/NLB. Control disabled to prevent false positives.”
	•	Store those justifications as “Management Responses” in the manual-evidence section of the SOC 2 assessment.

⸻

9.2.3  Revised Mapping of 28 Automatable Controls

Below we map each SOC 2 criterion to the specific AWS-managed control. Controls outside FSBP/CIS are deliberately omitted—we want zero custom rules.

SOC 2 Ref	Condensed Description	AWS Check	Standard	Status in FAFO
CC 6.1.2	MFA enforced	IAM.5 / IAM.6	FSBP	Enabled
CC 6.1.3	Strong password policy	IAM.1 / IAM.2	FSBP	Enabled
CC 6.1.4	Inbound ports restricted	vpc-sg-open-only-to-authorized-ports	CIS Pack	Enabled
CC 6.1.6	TLS everywhere	ELB.1 / CloudFront.1	FSBP	Enabled
CC 6.1.7	DB encryption	RDS.1	FSBP	Enabled
CC 6.1.8	Key rotation	kms-key-rotation-enabled	KMS Pack	Enabled
CC 6.1.9	RBAC via groups	IAM.3	FSBP	Enabled
CC 6.1.10	Data-at-rest encryption	S3.2 / EBS.1 / RDS.3	FSBP	Enabled
CC 6.2.1	Admin access limited	IAM.4	FSBP	Enabled
CC 6.6.2	Security monitoring active	GuardDuty	FSBP	Enabled
CC 6.6.3	IDS / IPS	GuardDuty + VPC.1	FSBP	Enabled
CC 6.6.4	Log aggregation (SIEM)	CloudTrail.2 / CloudWatch.5	FSBP	Enabled
CC 7.2 – Network Scan	Monthly vuln scans	Git → ASFF	Git Integration	Enabled
CC 7.2 – DAST	Dynamic app scans	Git → ASFF	Git Integration	Enabled
CC 7.2 – Container	ECR image scans	ECR.1	FSBP	Enabled
CC 8.1.3	Version control with RBAC	Git evidence	Git Integration	Enabled
CC 8.1.5	Static code scan	Git → ASFF	Git Integration	Enabled
CC 8.1.7	Approved change	CodePipeline approvals	-	Enabled
CC 8.1.9	Deploy alerts	CloudWatch.14	CIS	Enabled
CC 9.1.3	Cross-AZ backups	rds-automatic-backup-enabled	CIS	Enabled
A 1.1.1	Capacity monitoring	EC2.8 + CloudWatch alarms	FSBP	Enabled
A 1.1.2	Auto-scaling	autoscaling-group-elb-healthcheck-required	CIS	Enabled
A 1.2.1	Backup failure alerts	Backup.1	FSBP	Enabled
A 1.2.3	Multi-AZ architecture	rds-multi-az-support	CIS	Enabled
C 1.1.3	Data inventory review	Manual	–	Out of scope
CC 6.7.1	Data-loss prevention	Manual	–	Out of scope
A1.2.4/5/6	Physical / BMS controls	Manual	–	Out of scope

Noise-reduction note
ELB.3 (classic ELB logging) and EKS.2 (EKS control plane logging) exist in FSBP but FAFO does not run those services. We disable them to keep Security Hub scores meaningful.

⸻

9.2.4  Collaborating With Security Ops
	•	Kick-off meeting – 30 minutes. Explain why certain controls are disabled and show the mapping spreadsheet.
	•	Slack channel #soc2-signals – every new Security Hub or Config critical finding posts here; SecOps triages, GRC observes.
	•	Monthly architecture review – if the product team adopts a new AWS service (e.g., Redshift), we revisit which controls to enable.

Outcome: Security owns alert response, GRC owns evidence curation—and neither team feels blindsided.

⸻

In the next section we will:
	1.	Build the Python GitLab-to-ASFF converter line-by-line.
	2.	Wire an EventBridge rule that scoops new findings into Audit Manager automatically.
	3.	Walk through the Friday Excel Lambda: from querying evidence to formatting workbooks and publishing to S3.

By the end you’ll see how 25 native AWS checks plus three lightweight Git integrations cut FAFO’s “audit meeting” count from 15 to two—intro and closing call.