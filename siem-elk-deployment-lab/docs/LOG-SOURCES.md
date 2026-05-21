# SIEM Log Sources & Parsing Guide

## Overview
This document describes the log sources ingested into the SIEM and the parsing methods used to make logs searchable and actionable.

## Supported Log Sources
- Apache / Nginx web server logs
- System logs (Syslog, systemd)
- Windows Event Logs
- Firewall and IDS logs
- Application logs (JSON and text)
- Database audit logs
- Cloud logs (AWS CloudTrail)

## Apache / Nginx Logs
### Log Format
- Apache Combined Log Format
- Nginx access log format

### Parsing Method
- Use Logstash `grok` with `%{COMBINEDAPACHELOG}` or custom patterns
- Extract fields: `clientip`, `request`, `status`, `bytes`, `referrer`, `agent`
- Normalize to ECS fields: `source.ip`, `http.request.method`, `http.response.status_code`

### Use Cases
- Detect SQL injection and XSS request payloads
- Identify suspicious user agents
- Track high-volume request sources

## Syslog / System Logs
### Log Format
- Standard syslog messages: `<PRI>timestamp host program[pid]: message`
- Systemd journal export to syslog-compatible format

### Parsing Method
- Use Logstash `grok` with `SYSLOGBASE` or `SYSLOG5424LINE`
- Extract fields: `program`, `pid`, `severity`, `message`
- Map severity values to ECS `log.level`

### Use Cases
- Detect authentication failures
- Monitor service restarts and configuration changes
- Correlate system events with user sessions

## Windows Event Logs
### Log Format
- Winlogbeat JSON events from Windows Event Log channels

### Parsing Method
- Use Winlogbeat module to ship events
- Use Logstash `json` parsing if needed
- Extract fields: `event.code`, `event.provider`, `winlog.event_data`, `user.name`

### Use Cases
- Detect privilege escalation (Event ID 4672)
- Detect account lockouts and failed logons
- Monitor Windows security policy changes

## Application Logs
### Log Format
- JSON log lines or structured text
- Custom application event schemas

### Parsing Method
- Use Logstash `json` filter for structured logs
- Use `grok` for text logs with custom patterns
- Extract fields: `event.type`, `transaction.id`, `user.id`, `status`

### Use Cases
- Track business transaction failures
- Detect application errors and exceptions
- Monitor authentication and authorization events

## Cloud Logs (AWS CloudTrail)
### Log Format
- JSON events from CloudTrail

### Parsing Method
- Use Filebeat or Logstash JSON parser
- Extract fields: `eventName`, `eventSource`, `userIdentity`, `sourceIPAddress`

### Use Cases
- Detect suspicious console login attempts
- Track AWS IAM policy changes
- Monitor resource creation and deletion

## Database Logs
### Log Format
- MySQL/PostgreSQL audit logs
- SQL query logs, error logs

### Parsing Method
- Use Filebeat to ship log files
- Use `grok` patterns for SQL log entries
- Extract fields: `query`, `user`, `database`, `status`

### Use Cases
- Detect failed authentication attempts
- Identify suspicious query patterns
- Monitor database schema changes

## Data Enrichment
- GeoIP lookup for source IP addresses
- Threat intelligence feeds for malicious IP identification
- User agent parsing for device classification
- Static metadata enrichment for host and application tags
