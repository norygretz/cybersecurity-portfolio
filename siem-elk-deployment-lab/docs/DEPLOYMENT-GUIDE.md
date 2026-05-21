# SIEM Deployment Guide

## Overview
This document describes the deployment steps for the SIEM ELK Stack solution, including Elasticsearch, Logstash, Kibana, and Beats. The goal is a secure, scalable deployment for log aggregation, search, and detection.

## Deployment Strategy
- Deploy Elasticsearch on multiple nodes for redundancy and performance
- Deploy Logstash as a centralized ingestion layer
- Deploy Kibana as the visualization interface
- Deploy Beats on endpoints to forward logs
- Use TLS encryption between components
- Enable Elasticsearch security and access control

## Pre-Deployment Checklist
- [ ] Provision 3 or more Linux servers (recommended Ubuntu 22.04)
- [ ] Allocate at least 8GB RAM and 2 CPUs per node
- [ ] Install Java 11+ on all nodes
- [ ] Open necessary ports: 9200, 9300, 5044, 5601, 5140, 5000
- [ ] Prepare TLS certificates for Elasticsearch and Logstash
- [ ] Configure system clocks to use NTP
- [ ] Configure disk storage for Elasticsearch indices and backups

## Installation Steps

### 1. Install Elasticsearch
1. Download the Elasticsearch tarball or package.
2. Extract to `/usr/share/elasticsearch`.
3. Copy `elasticsearch.yml` to `/etc/elasticsearch/elasticsearch.yml`.
4. Set ownership: `chown -R elasticsearch:elasticsearch /etc/elasticsearch`
5. Configure JVM heap in `jvm.options` to 50% of available RAM.
6. Start Elasticsearch: `systemctl start elasticsearch`.
7. Validate: `curl -k https://localhost:9200`.

### 2. Install Kibana
1. Download Kibana tarball or package.
2. Copy `kibana.yml` to `/etc/kibana/kibana.yml`.
3. Configure Kibana to talk to Elasticsearch over TLS.
4. Start Kibana: `systemctl start kibana`.
5. Validate: `curl -k https://localhost:5601`.

### 3. Install Logstash
1. Download and extract Logstash.
2. Copy `logstash-main.conf` to `/etc/logstash/conf.d/logstash-main.conf`.
3. Copy filter files into `/etc/logstash/conf.d/filters/`.
4. Configure certificate paths and Elasticsearch credentials.
5. Start Logstash: `systemctl start logstash`.
6. Validate logs appear in Elasticsearch.

### 4. Install Beats
1. Install Filebeat on Linux web and app servers.
2. Install Winlogbeat on Windows hosts.
3. Copy `filebeat.yml` to `/etc/filebeat/filebeat.yml`.
4. Enable modules for system, Apache, and Nginx logs.
5. Start Filebeat/Winlogbeat.
6. Validate shipping by checking Kibana Discover.

## Post-Deployment Configuration
- Configure Kibana index patterns for `logstash-*`
- Import dashboards and saved searches
- Create user roles and assign RBAC permissions
- Configure alerting channels (email, Slack, webhook)
- Enable index lifecycle management (ILM)
- Schedule snapshot backups for Elasticsearch

## Operational Best Practices
- Monitor disk utilization and heap usage
- Rotate TLS certificates before expiration
- Maintain a separate logging network segment
- Use dedicated nodes for master, ingest, and data roles
- Regularly test alert rules and incident workflows
- Protect access to Kibana with MFA if available
