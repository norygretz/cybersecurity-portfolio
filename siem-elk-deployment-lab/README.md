# SIEM Log Management & Threat Detection Lab

## Executive Summary

This project demonstrates **enterprise-grade Security Information and Event Management (SIEM)** deployment using the **ELK Stack (Elasticsearch, Logstash, Kibana)**. The lab includes comprehensive log ingestion from multiple sources, real-time correlation rules, threat detection dashboards, and security alerting capabilities suitable for small-to-medium enterprise SOC operations.

**Portfolio Value:** Demonstrates security operations expertise, log analysis capabilities, alert creation, threat detection, compliance monitoring, and infrastructure observability aligned with **NIST SP 800-92 (Log Management)** and **CIS Controls (Detection & Analysis)**.

---

## Project Structure

```
siem-elk-deployment-lab/
├── README.md (this file)
├── docs/
│   ├── ARCHITECTURE.md           # ELK Stack design & components
│   ├── DEPLOYMENT-GUIDE.md       # Installation & configuration steps
│   ├── LOG-SOURCES.md            # Data ingestion & log parsing
│   ├── ALERTS-RULES.md           # Detection rules & correlation
│   ├── DASHBOARDS-GUIDE.md       # Kibana visualization & reporting
│   └── USE-CASES.md              # Real-world security scenarios
├── configs/
│   ├── elasticsearch.yml         # Elasticsearch configuration
│   ├── kibana.yml                # Kibana configuration
│   ├── logstash-main.conf        # Main Logstash pipeline
│   ├── logstash-filters/         # Logstash filter plugins
│   │   ├── apache.conf
│   │   ├── syslog.conf
│   │   ├── windows.conf
│   │   └── application.conf
│   └── filebeat.yml              # Filebeat configuration
├── dashboards/
│   ├── security-overview.json    # Main security dashboard
│   ├── threat-detection.json     # Threat detection dashboard
│   ├── compliance-monitoring.json # Compliance dashboard
│   └── infrastructure-health.json # System health dashboard
└── alerts/
    ├── intrusion-detection.json  # IDS alert rules
    ├── compliance-violations.json # Policy violation alerts
    ├── system-anomalies.json     # Behavioral anomaly alerts
    └── threat-hunting.json       # Advanced threat hunting rules
```

---

## Quick Start: ELK Stack Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ or CentOS 8+): minimum 8GB RAM, 2 CPU cores
- Java Runtime Environment (JRE) 11 or higher
- Disk space: 100GB+ for log storage (depending on volume)
- Network: Open ports 5601 (Kibana), 9200 (ES API), 5000 (Logstash)

### Installation Overview

```bash
# Step 1: Install Elasticsearch (centralized log storage & search engine)
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.0.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.0.0-linux-x86_64.tar.gz
./elasticsearch/bin/elasticsearch

# Step 2: Install Kibana (data visualization & dashboard interface)
wget https://artifacts.elastic.co/downloads/kibana/kibana-8.0.0-linux-x86_64.tar.gz
tar -xzf kibana-8.0.0-linux-x86_64.tar.gz
./kibana/bin/kibana

# Step 3: Install Logstash (log ingestion, parsing, transformation)
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.0.0-linux-x86_64.tar.gz
tar -xzf logstash-8.0.0-linux-x86_64.tar.gz
./logstash/bin/logstash -f logstash.conf

# Step 4: Install Beats (lightweight log shippers from endpoints)
# Filebeat: Ships log files
# Metricbeat: Ships system metrics
# Winlogbeat: Ships Windows Event Logs (on Windows systems)
```

### Access the Dashboard
- **Kibana Dashboard:** http://localhost:5601
- **Default credentials:** elastic / [generated password]
- **First login:** Set up index patterns for log discovery

---

## Architecture Overview: ELK Stack Components

```
┌──────────────────────────────────────┐
│         DATA SOURCES                 │
├──────────────────────────────────────┤
│ • Web Servers (Apache, Nginx)        │
│ • Application Logs (Custom apps)     │
│ • System Logs (Syslog/Systemd)       │
│ • Windows Events (Security, System)  │
│ • Network Devices (Firewalls, IDS)   │
│ • Cloud Logs (AWS CloudTrail)        │
│ • Database Logs (MySQL, PostgreSQL)  │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│     BEATS (Log Shippers)             │
├──────────────────────────────────────┤
│ • Filebeat: Lightweight file shipper │
│ • Metricbeat: System metrics         │
│ • Winlogbeat: Windows Event logs     │
│ • Packetbeat: Network traffic        │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│    LOGSTASH (Log Processing)         │
├──────────────────────────────────────┤
│ Input:   Receive from Beats/Syslog  │
│ Filter:  Parse, enrich, correlate   │
│ Output:  Send to Elasticsearch      │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  ELASTICSEARCH (Search & Index)      │
├──────────────────────────────────────┤
│ • Full-text search engine            │
│ • Stores indexed documents           │
│ • Provides REST API for queries      │
│ • Supports replication & clustering  │
│ • TTL policies for data retention    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│    KIBANA (Visualization & UI)       │
├──────────────────────────────────────┤
│ • Interactive dashboards             │
│ • Advanced searching & filtering     │
│ • Alerts & anomaly detection         │
│ • Canvas for custom visualizations   │
│ • Machine learning for forecasting   │
└──────────────────────────────────────┘
```

---

## Log Sources & Data Ingestion

### Multi-Source Log Aggregation

```
Source Type          Protocol    Parser         Use Case
────────────────────────────────────────────────────────
Web Servers          Filebeat    grok           HTTP request analysis
System Logs          Syslog      grok, json     System event tracking
Windows Events       WinLogBeat  winlogbeat     Security audit logging
Firewall Logs        Syslog      grok           Network threat detection
IDS Alerts           TCP         json           Intrusion detection correlation
Application Logs     Filebeat    json, grok     Business transaction tracking
Database Logs        Filebeat    grok           Data access auditing
Cloud Logs (AWS)     CloudTrail  json           Infrastructure monitoring
```

### Example: Apache Web Server Log Ingestion

**Apache Combined Log Format:**
```
203.0.113.42 - username [21/May/2026:10:45:23 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
```

**Logstash Filter (grok parsing):**
```
grok {
  match => { "message" => "%{COMBINEDAPACHELOG}" }
}

# Extracts fields:
# - clientip: 203.0.113.42
# - ident: -
# - auth: username
# - timestamp: 21/May/2026:10:45:23 +0000
# - request: GET /api/users HTTP/1.1
# - response: 200
# - bytes: 1234
# - referrer: -
# - useragent: Mozilla/5.0
```

---

## Real-Time Threat Detection

### Alert Rule Examples

#### **Rule 1: Brute Force SSH Attack Detection**
```
Detection Logic:
  Source IP + Failed SSH logins (authentication:failure)
  Condition: >5 failures within 5 minutes
  Action: Alert + Block IP via firewall
  
Elasticsearch Query:
  {
    "query": {
      "bool": {
        "must": [
          { "term": { "service": "sshd" } },
          { "term": { "event.outcome": "failure" } }
        ]
      }
    },
    "aggs": {
      "by_source_ip": {
        "terms": {
          "field": "source.ip",
          "min_doc_count": 5
        }
      }
    }
  }
```

#### **Rule 2: SQL Injection Attack Pattern**
```
Detection Logic:
  HTTP request contains SQL keywords: UNION, SELECT, DROP, DELETE
  Pattern: ' OR '1'='1, SLEEP(), BENCHMARK()
  Source: Web application logs (access.log)
  
Alert Trigger:
  payload contains: ('.*(\bUNION\b|\bSELECT\b|\bDROP\b|' OR '1'='1)'
  Severity: HIGH (attempted data exfiltration)
  Action: Alert + WAF block
```

#### **Rule 3: Privilege Escalation Detection**
```
Detection Logic:
  Windows Event ID 4672 (Special Privileges Assigned)
  Target: Non-admin account gaining admin rights
  Condition: Unexpected privilege escalation pattern
  
Correlation:
  Match with user baseline:
    IF user never had admin rights THEN
    THEN alert "Unexpected privilege escalation"
```

#### **Rule 4: Data Exfiltration Detection**
```
Detection Logic:
  Source: firewall/proxy logs
  Outbound traffic volume > threshold
  Destination: known malicious IP or unusual domain
  Protocol: HTTPS (encrypted, but volume indicates exfil)
  
Alert Example:
  User "john.smith" transferred 5GB outbound
  Destination: 192.0.2.100 (known botnet C&C)
  Time: 2:47 AM (unusual hours)
  Severity: CRITICAL
```

---

## Kibana Dashboard: Security Operations Center (SOC)

### Main Security Dashboard Components

```
╔════════════════════════════════════════════════════════╗
║           SECURITY OPERATIONS DASHBOARD                ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  [METRIC] Critical Alerts (24h): 3                    ║
║  [METRIC] High Severity Events: 47                    ║
║  [METRIC] Failed Logins: 234                          ║
║  [METRIC] Blocked Connections: 1,203                  ║
║                                                        ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ Event Timeline (Last 24 Hours)                   │ ║
║  │ ▁▂▃▅▇▆▄▂▁▂▃▅▇▆▄▂▁▂▃▅▇▆▄▂▁▂▃▅▇▆▄▂ Events         │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                        ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ Top Attack Sources                               │ ║
║  │ 203.0.113.45    ●●●●●●●●●● 145 events           │ ║
║  │ 198.51.100.23   ●●●●●●●●   98 events            │ ║
║  │ 192.0.2.198     ●●●●●●     67 events            │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                        ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ Alert Severity Distribution                      │ ║
║  │ 🔴 Critical: 3   🟠 High: 47   🟡 Med: 234       │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                        ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ Service Status                                   │ ║
║  │ Elasticsearch: - Online (3 nodes, healthy)       │ ║
║  │ Logstash:      - Processing (12.5k events/sec)  │ ║
║  │ Kibana:        - Online (8 active users)         │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

### Threat Detection Dashboard

```
Malicious IPs Currently Active:
┌─────────────────┬──────────────┬──────────┬────────────┐
│ Source IP       │ Attack Type  │ Count    │ Severity   │
├─────────────────┼──────────────┼──────────┼────────────┤
│ 203.0.113.45    │ SSH Brute    │ 145      │ 🔴 HIGH    │
│ 198.51.100.23   │ SQL Injection│ 98       │ 🔴 HIGH    │
│ 192.0.2.198     │ Port Scan    │ 67       │ 🟠 MEDIUM  │
└─────────────────┴──────────────┴──────────┴────────────┘

Failed Authentication Patterns:
┌──────────────────┬──────────┬───────────────────────────┐
│ Target Service   │ Failures │ Attacker Profile          │
├──────────────────┼──────────┼───────────────────────────┤
│ SSH (port 22)    │ 2,143    │ Distributed (354 IPs)     │
│ RDP (port 3389)  │ 456      │ Single source (1 IP)      │
│ HTTP Auth        │ 234      │ Sequential IDs (bot-like)  │
└──────────────────┴──────────┴───────────────────────────┘
```

---

## Compliance & Security Monitoring

### PCI-DSS Log Requirements

```
PCI-DSS Requirement 10: Logging & Monitoring

Required Logs:
- User access to cardholder data
- Administrative actions
- Failed access attempts
- System resource use
- Invalid access attempts
- Authentication mechanisms use

SIEM Implementation:
├─ Elasticsearch indexes all required logs
├─ Kibana dashboards track compliance metrics
├─ Alerts fire on policy violations
├─ Reports auto-generate monthly
└─ Log retention: 1 year (90 days hot)
```

### NIST Framework Alignment

```
NIST CSF Category          SIEM Controls
────────────────────────────────────────────
IDENTIFY                   Asset inventory logs
PROTECT                    Access control logs
DETECT                     Alert rules & dashboards
RESPOND                    Incident tracking dashboard
RECOVER                    Backup & restore procedures
```

---

## Skills Demonstrated

- - **ELK Stack Deployment** - Elasticsearch, Logstash, Kibana installation & configuration
- - **Log Ingestion & Parsing** - Multi-source log collection and structured parsing
- - **Data Enrichment** - GeoIP lookups, threat intelligence integration
- - **Alert Creation** - Real-time detection rules for security events
- - **Threat Correlation** - Multi-field event correlation
- - **Dashboard Design** - Custom Kibana visualizations and reporting
- - **Security Monitoring** - SOC operations and incident detection
- - **Compliance Monitoring** - PCI-DSS, HIPAA, SOC 2 audit logs
- - **Machine Learning** - Anomaly detection and behavioral analysis
- - **Infrastructure Observability** - System health and performance monitoring
- - **Incident Response** - Alert investigation and triage
- - **Log Retention & Management** - Index lifecycle management, data archiving

---

## Technology Stack

### Core Components
- **Elasticsearch 8.0+** - Distributed search and analytics engine
- **Logstash 8.0+** - Data processing and transformation
- **Kibana 8.0+** - Data visualization and dashboarding
- **Beats** - Lightweight log shippers (Filebeat, Winlogbeat, Metricbeat)

### Deployment Infrastructure
- **Operating System** - Linux (Ubuntu/CentOS) or containerized (Docker/Kubernetes)
- **Java Runtime** - JRE 11+
- **Storage** - NAS or SAN for Elasticsearch indices
- **Networking** - Dedicated SIEM network segment, TLS encryption

### Integration Capabilities
- **Log Sources** - Apache, Nginx, Syslog, Windows Events, AWS CloudTrail, databases
- **Threat Intelligence** - AbuseIPDB, OTX, VirusTotal integration
- **Ticketing** - Jira, ServiceNow for incident management
- **Alerting** - Email, Slack, PagerDuty, webhook notifications
- **Cloud Platforms** - AWS CloudTrail logs, Azure Monitor logs

---

## Use Cases Covered

### 1. **Intrusion Detection**
- Brute force attack detection (repeated failed logins)
- Port scanning detection (SYN packets to multiple ports)
- Malware command & control (C&C) communication detection
- Botnet activity identification

### 2. **Compliance Monitoring**
- PCI-DSS requirement tracking
- HIPAA audit log verification
- SOC 2 control monitoring
- User access to sensitive data

### 3. **Incident Response**
- Rapid event timeline reconstruction
- Impact analysis (affected systems/users)
- Lateral movement detection (East-West traffic analysis)
- Evidence collection for forensics

### 4. **Threat Hunting**
- Advanced pattern matching
- Behavioral baseline anomalies
- Indicator of Compromise (IOC) searches
- Threat intelligence correlation

### 5. **Operational Monitoring**
- System resource utilization
- Service availability tracking
- Performance degradation alerts
- Capacity planning metrics

---

## Metrics & Performance

```
Performance Characteristics:
├─ Event Ingestion: 12,500+ events/second
├─ Search Response Time: <500ms (p95)
├─ Alert Detection Latency: <1 minute (median)
├─ Dashboard Load Time: <2 seconds
├─ Data Retention: 1 year hot+warm, unlimited cold
└─ Storage Efficiency: ~1KB per event (indexed)

Scalability:
├─ Elasticsearch cluster: 3+ nodes (horizontally scalable)
├─ Index size management: Auto-rollover daily
├─ Concurrent users: 100+ (Kibana)
└─ Geographic distribution: Multi-region capable
```

---

## Deployment Checklist

- [ ] Elasticsearch cluster installed and clustered
- [ ] Security enabled (X-Pack: authentication, encryption)
- [ ] Kibana authenticated and accessible
- [ ] Logstash pipelines configured for each log source
- [ ] Beats deployed to endpoint systems
- [ ] Index templates configured for auto-rollover
- [ ] Detection rules created and tested
- [ ] Dashboards created and shared with team
- [ ] Alerting configured (email/Slack/PagerDuty)
- [ ] Retention policies configured (1-year minimum)
- [ ] Backup/restore procedures documented
- [ ] Access controls implemented (RBAC in Kibana)
- [ ] Audit logging enabled
- [ ] Performance baseline established
- [ ] Team training completed
- [ ] Documentation handed off to operations

---

## Learning Outcomes

- - How SIEM systems aggregate and analyze security logs
- - ELK Stack architecture and component interactions
- - Log parsing techniques using Logstash filters
- - Real-time threat detection rule creation
- - Complex event correlation and pattern matching
- - Kibana visualization and dashboard design
- - Compliance monitoring implementation
- - Incident response workflow automation
- - Performance optimization for high-volume log ingestion
- - Security monitoring best practices

---

## Additional Resources

- [Elastic Stack Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-92.pdf)
- [CIS Controls V8: Detection and Analysis](https://www.cisecurity.org/controls/detection-and-analysis)
- [PCI-DSS Requirement 10: Logging and Monitoring](https://www.pcisecuritystandards.org/)
- [MITRE ATT&CK: Detection Engineering](https://mitre-attack.github.io/)
- [ELK Stack Tutorial & Best Practices](https://www.elastic.co/training)

---

## Version History

- **v1.0** - Initial SIEM deployment and threat detection lab documentation (2024)

---

## Educational Value

This lab demonstrates real-world security operations center (SOC) capabilities used by organizations to detect, investigate, and respond to security threats. By understanding log aggregation, parsing, correlation, and alerting, you develop expertise in one of the most critical security functions: threat detection and incident response. These skills are in high demand across all industries and are essential for security engineers, SOC analysts, and incident responders.
