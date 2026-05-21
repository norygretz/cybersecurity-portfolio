# AWS Security Implementation Checklist

## Pre-Deployment Security Checklist

### Identity & Access Management (IAM)

- [ ] Root account MFA enabled
- [ ] Root account access restricted
- [ ] No root account API keys
- [ ] Admin users limited (2-person rule)
- [ ] Cross-account access configured (if needed)
- [ ] Service roles created with least privilege
- [ ] Password policy enforced (14+ chars, complexity)
- [ ] MFA enforced for all human users
- [ ] Access keys rotated every 90 days
- [ ] Unused credentials deleted
- [ ] Session tokens have expiration
- [ ] CloudTrail enabled for IAM changes

### VPC & Network Security

- [ ] VPC created with appropriate CIDR block
- [ ] Public subnets created in multiple AZs
- [ ] Private subnets created for applications
- [ ] Database subnets created (private)
- [ ] NAT Gateways/Instances deployed
- [ ] Internet Gateway attached to VPC
- [ ] VPC Flow Logs enabled
- [ ] NACLs configured (if required)
- [ ] Security Groups created with minimum rules
- [ ] Network ACLs deny unnecessary traffic
- [ ] VPC endpoints configured (S3, DynamoDB)
- [ ] VPC peering configured (if needed)
- [ ] Route tables properly segmented
- [ ] Default Security Group restrictions

### Compute (EC2) Security

- [ ] Latest OS image selected
- [ ] EC2 instances in private subnets
- [ ] Security Groups restricting inbound traffic
- [ ] Security Groups restricting outbound traffic
- [ ] Bastion host for SSH access (if needed)
- [ ] Elastic IPs assigned for static external IPs
- [ ] CloudWatch monitoring enabled
- [ ] CloudWatch agent installed
- [ ] Systems Manager Session Manager enabled
- [ ] SSH keys secured (never shared)
- [ ] SSH key rotation policy
- [ ] EBS encryption enabled
- [ ] EBS snapshots encrypted
- [ ] Instance metadata service v2 (IMDSv2) enforced
- [ ] Termination protection enabled (production)
- [ ] Detailed monitoring enabled
- [ ] VPC endpoint security groups reviewed

### Database (RDS) Security

- [ ] Multi-AZ deployment enabled
- [ ] Database subnet group created
- [ ] DB Security Group restricting access
- [ ] Encryption at rest enabled (KMS)
- [ ] Encryption in transit enabled (SSL/TLS)
- [ ] Backup retention configured (30+ days)
- [ ] Backup encryption enabled
- [ ] Automated backups enabled
- [ ] Enhanced monitoring enabled
- [ ] Database port changed from default
- [ ] Master username not admin
- [ ] Strong master password enforced
- [ ] Database audit logging enabled
- [ ] Parameter group hardened
- [ ] Performance Insights enabled
- [ ] Cross-region read replicas created
- [ ] Deletion protection enabled

### Storage (S3) Security

- [ ] Bucket created with unique name
- [ ] Block Public Access enabled (all four settings)
- [ ] Versioning enabled
- [ ] MFA Delete enabled
- [ ] Server-side encryption enabled (SSE-S3 or SSE-KMS)
- [ ] Bucket policies reviewed (no public access)
- [ ] IAM policies reviewed for least privilege
- [ ] Access logging enabled
- [ ] CloudTrail logging enabled
- [ ] Lifecycle policies configured
- [ ] Cross-region replication enabled (DR)
- [ ] Bucket notifications configured
- [ ] CORS configuration restricted
- [ ] SSL/TLS required for uploads
- [ ] Object locking configured (if required)

### Application Load Balancer (ALB) Security

- [ ] ALB deployed in public subnets (multiple AZs)
- [ ] Security Groups restricting access
- [ ] SSL/TLS certificate installed
- [ ] TLS 1.2+ enforced
- [ ] Weak cipher suites disabled
- [ ] HTTPS listener created (port 443)
- [ ] HTTP listener redirects to HTTPS
- [ ] Access logs enabled (S3)
- [ ] WAF attached
- [ ] Shield Standard enabled (automatic)
- [ ] Health check configured
- [ ] Stickiness configured (if needed)
- [ ] Cross-zone load balancing enabled
- [ ] Deletion protection enabled

### Logging & Monitoring

- [ ] CloudTrail enabled (all regions)
- [ ] CloudTrail logs stored in S3
- [ ] CloudTrail log encryption enabled
- [ ] CloudTrail log integrity validation enabled
- [ ] CloudWatch Logs group created
- [ ] Log retention configured (30+ days)
- [ ] Log encryption enabled
- [ ] CloudWatch alarms configured
- [ ] SNS topic for notifications
- [ ] Email subscriptions to SNS
- [ ] CloudWatch dashboard created
- [ ] VPC Flow Logs enabled
- [ ] Application logs aggregated
- [ ] Log analysis automated (Athena, Splunk)

### Security Services

- [ ] AWS WAF rules configured
- [ ] Rate limiting enabled
- [ ] IP whitelist/blacklist configured
- [ ] AWS Shield activated
- [ ] GuardDuty enabled
- [ ] GuardDuty findings reviewed
- [ ] AWS Config enabled
- [ ] Config rules for compliance
- [ ] Config remediation configured
- [ ] AWS Inspector scans scheduled
- [ ] Inspector findings reviewed
- [ ] Systems Manager Patch Manager enabled
- [ ] Patch baselines created
- [ ] Patch compliance monitored

### Encryption & Key Management

- [ ] KMS master key created
- [ ] KMS key alias created
- [ ] Key rotation enabled
- [ ] Key policy reviewed (principle of least privilege)
- [ ] CloudHSM deployed (if required)
- [ ] Secrets Manager configured
- [ ] Secrets rotation enabled
- [ ] Certificate Manager used (not self-signed)
- [ ] Certificate auto-renewal enabled
- [ ] Private key protection enforced

### Backup & Disaster Recovery

- [ ] Backup strategy documented
- [ ] RDS automated backups enabled
- [ ] Backup retention verified
- [ ] EBS snapshots scheduled
- [ ] S3 cross-region replication enabled
- [ ] Backup encryption enabled
- [ ] Backup testing schedule created
- [ ] DR region configured
- [ ] DNS failover configured (Route 53)
- [ ] RTO/RPO defined and documented
- [ ] Failover runbook created
- [ ] Failover drill scheduled

### Compliance & Auditing

- [ ] Compliance requirements identified
- [ ] Security policy documented
- [ ] Audit schedule created
- [ ] Compliance gaps identified
- [ ] Remediation plan created
- [ ] Third-party audit scheduled
- [ ] PCI-DSS compliance checked
- [ ] HIPAA compliance checked (if applicable)
- [ ] SOC 2 assessment scheduled
- [ ] Incident response plan documented
- [ ] Incident response team trained

### Operational Security

- [ ] Change management process
- [ ] Approval workflow for changes
- [ ] Rollback plan documented
- [ ] Runbooks created for common tasks
- [ ] On-call rotation established
- [ ] Escalation procedures documented
- [ ] Communication plan for incidents
- [ ] Post-incident review process

### Cost & Performance

- [ ] Budget alerts configured
- [ ] Anomaly detection enabled
- [ ] Resource tagging standardized
- [ ] Reserved Instances optimized
- [ ] Spot Instances evaluated
- [ ] Data transfer costs reviewed
- [ ] Performance baseline established
- [ ] Auto-scaling policies configured
- [ ] Cost optimization review scheduled

## Post-Deployment Verification

### Security Validation

```bash
# Verify S3 bucket public access blocked
aws s3api get-bucket-acl --bucket my-bucket

# Verify EC2 security groups
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,IpPermissions]'

# Verify CloudTrail enabled
aws cloudtrail describe-trails --region us-east-1

# Verify VPC Flow Logs
aws ec2 describe-flow-logs --filter Name=resource-type,Values=VPC

# Verify RDS encryption
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted]'
```

### Compliance Verification

```bash
# Check AWS Config compliance
aws configservice describe-compliance-by-config-rule

# Check GuardDuty findings
aws guardduty list-findings --detector-id <detector-id>

# Check SecurityHub findings
aws securityhub get-findings --max-results 100
```

---

**Checklist Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Ready for Review
