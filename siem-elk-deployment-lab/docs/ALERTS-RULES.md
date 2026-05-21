# SIEM Alert Rules & Detection Logic

## Overview
This document describes detection rules used in the SIEM to identify security threats, anomalies, and policy violations.

## Alert Rule Categories
- Brute force and credential abuse
- Web application attacks
- Privilege escalation
- Data exfiltration
- Suspicious system behavior
- Compliance violation alerts

## Rule 1: SSH Brute Force Detection
### Detection Logic
- Source: SSH authentication logs
- Condition: More than 5 failed login attempts from the same IP within 5 minutes
- Severity: High

### Example Query
```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "service": "sshd" } },
        { "term": { "event.outcome": "failure" } },
        { "range": { "@timestamp": { "gte": "now-5m" } } }
      ]
    }
  },
  "aggs": {
    "by_source_ip": {
      "terms": { "field": "source.ip", "min_doc_count": 5 }
    }
  }
}
```

## Rule 2: SQL Injection Detection
### Detection Logic
- Source: Web server logs
- Condition: HTTP request payload contains SQL keywords and suspicious patterns
- Severity: Critical

### Alert Criteria
- `http.request.uri` contains `UNION`, `SELECT`, `DROP`, `DELETE`, `' OR '1'='1'`
- `http.response.status_code` is 403 or 500

## Rule 3: Cross-Site Scripting (XSS) Detection
### Detection Logic
- Source: Web server logs
- Condition: URL or query contains script tags or JavaScript payloads
- Severity: High

### Alert Criteria
- `http.request.uri` contains `script`, `javascript:`, `onerror`, `alert(`
- Request originates from external/untrusted source

## Rule 4: Privilege Escalation Detection
### Detection Logic
- Source: Windows Security logs
- Condition: Event ID 4672 and user account not normally privileged
- Severity: High

### Alert Criteria
- `winlog.event_id` == 4672
- `user.name` not in admin baseline list
- Event occurs outside business hours or from a remote host

## Rule 5: Data Exfiltration Detection
### Detection Logic
- Source: Firewall or proxy logs
- Condition: Large outbound volume combined with suspicious IP or domain
- Severity: Critical

### Alert Criteria
- `direction` == `outbound`
- `bytes_out` >= 1,000,000,000
- Destination IP / domain matches threat intelligence list

## Rule 6: Compliance Violation Alert
### Detection Logic
- Source: Audit and access logs
- Condition: Access to sensitive data without required controls
- Severity: High

### Alert Criteria
- `event.action` == `data_access`
- `user.role` != `authorised_user`
- `data.classification` == `PII` or `Payment Card`

## Notification & Response
- Send email to SOC team for high/critical alerts
- Post alerts to Slack or Microsoft Teams channel
- Open incident ticket in JIRA or ServiceNow
- Correlate alerts with historical context for false positives

## Tuning Notes
- Start with broad detection rules, then tune thresholds using normal baseline traffic
- Suppress known benign sources (internal monitoring, health checks)
- Use tagging to classify alerts by type and severity
- Maintain a false-positive review process with quarterly tuning
