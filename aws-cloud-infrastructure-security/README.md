# AWS Cloud Infrastructure Security Design

## Executive Summary

This portfolio project demonstrates a **secure, scalable, and production-ready AWS cloud infrastructure** implementing industry best practices for:

- **Multi-tier architecture** with proper network segmentation
- **Identity & access management** (IAM) with principle of least privilege
- **Data protection** at rest and in transit
- **Compliance** with security frameworks (PCI-DSS, HIPAA)
- **High availability** and disaster recovery
- **Cost optimization** with security considerations

## Project Overview

This project documents the design, implementation, and security hardening of a complete AWS cloud environment serving a global e-commerce platform with:

- **Traffic**: 1M+ daily active users
- **Regions**: Multi-region deployment (Primary + DR)
- **Services**: 15+ AWS services integrated
- **Security**: Defense-in-depth approach

## Architecture Components

### 1. Network Architecture (VPC)

```
AWS Account
└─ VPC (10.0.0.0/16)
   ├─ Public Subnets
   │  ├─ AZ-A: 10.0.1.0/24 (NAT Gateway, ALB)
   │  └─ AZ-B: 10.0.2.0/24 (NAT Gateway, ALB)
   │
   ├─ Private Subnets (Applications)
   │  ├─ AZ-A: 10.0.11.0/24 (EC2 Instances)
   │  └─ AZ-B: 10.0.12.0/24 (EC2 Instances)
   │
   ├─ Database Subnets
   │  ├─ AZ-A: 10.0.21.0/24 (RDS Primary)
   │  └─ AZ-B: 10.0.22.0/24 (RDS Standby)
   │
   └─ Management Subnets
      ├─ AZ-A: 10.0.31.0/24 (Bastion Host)
      └─ AZ-B: 10.0.32.0/24 (Bastion Standby)
```

**Security Controls**:
- Network ACLs (NACLs) for stateless filtering
- Security Groups for stateful filtering
- VPC Flow Logs for network monitoring
- Private subnets for sensitive workloads

### 2. Compute Layer

**Load Balancing**:
- Application Load Balancer (ALB) in public subnets
- TLS/SSL termination at ALB
- Health checks for auto-healing
- Cross-AZ failover

**Application Servers**:
- EC2 instances in private subnets
- Auto Scaling Group (ASG) for elasticity
- Min: 2, Max: 10 instances
- CloudWatch monitoring

**Container Orchestration** (Optional):
- Amazon ECS for containerized workloads
- ECR for private Docker registry
- Fargate for serverless containers

### 3. Database Layer

**Primary Database**:
- Amazon RDS for MySQL 8.0
- Multi-AZ deployment
- Automated backups (35-day retention)
- Encrypted with AWS KMS
- Enhanced monitoring enabled

**Database Security**:
- Security Groups limiting access to app tier only
- Encryption at rest (KMS)
- Encryption in transit (SSL/TLS)
- VPC endpoint for private connectivity

**Backup & Disaster Recovery**:
- Automated snapshots
- Cross-region replication
- Point-in-time recovery (PITR)
- Automated failover (RTO: 5 min, RPO: 1 min)

### 4. Storage

**Object Storage**:
- S3 buckets for static content
- Versioning enabled
- Server-side encryption (SSE-S3)
- CloudFront distribution for edge caching
- Bucket policies restricting public access

**Encryption Strategy**:
- Transit: CloudFront (HTTPS/TLS 1.2+)
- Rest: AES-256 encryption
- Key management: AWS KMS

### 5. Identity & Access Management (IAM)

**Principle of Least Privilege**:

```
└─ Root Account
   ├─ Admin Users (2-person rule)
   ├─ Developer Role
   │  └─ EC2, Lambda, CloudWatch access
   ├─ DevOps Role
   │  └─ Infrastructure, RDS, S3 access
   ├─ Database Admin Role
   │  └─ RDS, backup, replication
   └─ Security Audit Role
      └─ Read-only across all services
```

**Key Policies**:
- MFA required for console access
- Temporary credentials only (no long-term keys)
- IP restrictions where applicable
- Service-specific roles for applications

### 6. Monitoring & Logging

**CloudWatch Monitoring**:
- CPU utilization
- Memory usage
- Network I/O
- Disk space
- Application logs
- Custom metrics

**Centralized Logging**:
- VPC Flow Logs → S3
- ALB Access Logs → S3
- CloudTrail audit logs → S3 + CloudWatch
- Application logs → CloudWatch Logs
- Log retention: 30+ days

**Alerting**:
- Critical alerts: SNS + email + Slack
- Warning alerts: Slack channel
- Escalation policies for on-call
- Runbook for common incidents

### 7. Security Services

**AWS WAF** (Web Application Firewall):
- SQL injection protection
- XSS prevention
- DDoS protection (Shield)
- Bot control
- Rate limiting

**AWS GuardDuty**:
- Threat detection
- Compromised EC2 detection
- Unusual API calls
- Findings → CloudWatch → SNS

**AWS Config**:
- Compliance tracking
- Configuration changes
- Remediation automation
- Audit trail

## Network Security

### Network Segmentation

```
Internet
   │ (Port 443/80)
   ▼
┌──────────────────────────┐
│  AWS WAF + CloudFront    │
└──────────────┬───────────┘
               │ (Port 443)
               ▼
┌──────────────────────────┐
│  Application Load        │
│  Balancer (Public)       │
└──────────────┬───────────┘
               │ (Port 8080)
               ▼
┌──────────────────────────┐
│  EC2 Instances           │
│  (Private Subnet)        │
└──────────────┬───────────┘
               │ (Port 3306)
               ▼
┌──────────────────────────┐
│  RDS Database            │
│  (Private Subnet)        │
└──────────────────────────┘
```

### Security Group Rules

| Layer | Source | Protocol | Port | Purpose |
|-------|--------|----------|------|---------|
| ALB | 0.0.0.0/0 | TCP | 443 | HTTPS |
| ALB | 0.0.0.0/0 | TCP | 80 | HTTP (redirect) |
| EC2 | ALB SG | TCP | 8080 | App traffic |
| EC2 | Bastion SG | TCP | 22 | SSH admin |
| RDS | EC2 SG | TCP | 3306 | Database |
| RDS | Bastion SG | TCP | 3306 | DB admin |

## Data Protection

### Encryption Standards

| Layer | Method | Key Type |
|-------|--------|----------|
| Transmission (TLS) | TLS 1.2+ | X.509 certificates |
| S3 Objects | AES-256 SSE | KMS keys |
| RDS Database | AES-256 | KMS keys |
| Snapshots | AES-256 | KMS keys |
| EBS Volumes | AES-256 | KMS keys |

### Key Management (AWS KMS)

- Master key in AWS CloudHSM
- Application keys rotated annually
- Automatic key rotation enabled
- Cross-account key access denied
- Key usage audited via CloudTrail

## Compliance & Standards

### Security Frameworks

| Framework | Requirement | Implementation |
|-----------|------------|-----------------|
| PCI-DSS 3.2.1 | Network segmentation | VPC + NACLs + SGs |
| PCI-DSS 3.2.1 | Encryption | TLS + KMS |
| HIPAA | Audit logging | CloudTrail + VPC Flow Logs |
| HIPAA | Access control | IAM + MFA |
| HIPAA | Incident response | CloudWatch + GuardDuty |

### Compliance Testing

- Quarterly penetration testing
- Annual third-party audit
- Continuous Config compliance
- Automated remediation for non-compliance

## Disaster Recovery & Business Continuity

### RTO/RPO Targets

| Component | RTO | RPO | Method |
|-----------|-----|-----|--------|
| Application | 30 min | 5 min | ASG + ALB |
| Database | 5 min | 1 min | RDS Multi-AZ |
| Data | 1 hour | 5 min | Automated snapshots |
| Configuration | 30 min | 0 | Infrastructure as Code |

### Backup Strategy

```
Daily Backup
├─ Automated RDS snapshots (35-day retention)
├─ S3 versioning (unlimited)
├─ Cross-region replication
├─ Encrypted with KMS
└─ Tested monthly via recovery drill
```

### Failover Automation

```
Primary Region Down
    ↓
Route53 health check fails
    ↓
DNS failover to secondary region
    ↓
CloudFormation stack creation in DR region
    ↓
RDS read replica promoted to primary
    ↓
ALB traffic redirected
    ↓
Application online in DR region
```

## Cost Optimization

### Reserved Instances

- Production: 70% RI coverage
- Savings: 40% vs On-Demand
- 3-year commitments for base load

### Auto Scaling Policies

```
CPU > 70%     → Scale up 2 instances
CPU < 30%     → Scale down 1 instance
Memory > 80%  → Alert + Scale up
NetworkIn > 5Gbps → Scale up
```

### Cost Monitoring

- Budget alerts at 50%, 80%, 100%
- Cost anomaly detection
- Resource tagging for chargeback
- Regular cost optimization review

## Implementation Timeline

| Phase | Duration | Activities |
|-------|----------|-----------|
| Design & Planning | 1 week | Architecture review, security assessment |
| Implementation | 3 weeks | VPC, EC2, RDS, IAM setup |
| Security Hardening | 2 weeks | WAF, GuardDuty, logging, monitoring |
| Testing | 2 weeks | Load testing, failover testing, security test |
| Production Deployment | 1 week | Migration, monitoring, tuning |

## Success Metrics

- **Availability**: 99.95% (52 minutes downtime/year)  
- **Performance**: <200ms response time (p95)  
- **Security**: Zero compliance violations  
- **Cost**: Within 10% of budget  
- **Scalability**: Handles 3x traffic spike automatically  

## Ongoing Operations

### Daily Tasks

- Monitor CloudWatch dashboards
- Review security alerts
- Check ASG scaling events
- Verify backup completion

### Weekly Tasks

- Cost analysis review
- Security patch assessment
- Log analysis for anomalies
- Capacity planning review

### Monthly Tasks

- DR failover drill
- Compliance status review
- Performance optimization
- Security training update

## Team Responsibilities

| Role | Responsibilities |
|------|-----------------|
| Cloud Architect | Design, standards, optimization |
| DevOps Engineer | Automation, CI/CD, infrastructure |
| Security Engineer | Compliance, monitoring, incident response |
| Database Admin | Backups, performance, replication |

## Future Enhancements

1. **Multi-region active-active** for lower RTO/RPO
2. **Kubernetes (EKS)** for container orchestration
3. **Machine Learning** for anomaly detection
4. **Serverless architecture** (Lambda, API Gateway)
5. **Advanced threat detection** with GuardDuty ML

---

**Document Version**: 1.0  
**Last Updated**: May 2026  
**Classification**: Technical Reference  
**Status**: Production Deployed
