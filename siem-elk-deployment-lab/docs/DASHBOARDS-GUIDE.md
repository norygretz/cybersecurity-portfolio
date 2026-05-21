# Kibana Dashboards & Visualization Guide

## Overview
This document describes the Kibana dashboard designs for security monitoring, threat detection, compliance, and infrastructure health.

## Dashboard Types
- Security Overview
- Threat Detection
- Compliance Monitoring
- Infrastructure Health

## Security Overview Dashboard
### Key Widgets
- Critical alerts count
- High severity event count
- Failed login trend
- Top attack sources
- Alert severity distribution
- Elasticsearch cluster health

### Purpose
Provide SOC analysts and managers with a single view of active security issues and system health.

## Threat Detection Dashboard
### Key Widgets
- Attack type breakdown (SQL injection, XSS, brute force)
- Top malicious source IPs
- Event timeline for active alerts
- Affected assets summary
- Geo map of attack origins

### Purpose
Highlight active threat patterns and help analysts focus on incidents with highest impact.

## Compliance Monitoring Dashboard
### Key Widgets
- PCI-DSS audit log coverage
- HIPAA log access events
- Policy violation count
- User access review summary
- Data retention index status

### Purpose
Track regulatory compliance for logging and monitoring controls.

## Infrastructure Health Dashboard
### Key Widgets
- Elasticsearch node CPU and memory usage
- Logstash event processing rate
- Kibana user sessions
- Disk utilization for hot/warm tiers
- Log ingestion latency

### Purpose
Ensure the SIEM platform remains healthy and performant.

## Best Practices
- Use filters to narrow dashboards by environment, host, or application
- Set refresh interval to 10 seconds for live monitoring
- Share dashboards with stakeholders using Kibana spaces
- Export snapshots for quarterly reporting
- Build drill-down dashboards for incident investigation

## Visualization Types
- Metric panels for counters and ratios
- Time series charts for trends
- Data tables for top sources and incidents
- Maps for geographic analysis
- Heat maps for volume distribution
- Gauge panels for health metrics
