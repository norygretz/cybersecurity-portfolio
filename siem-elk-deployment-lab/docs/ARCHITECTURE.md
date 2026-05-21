# ELK Stack Architecture & Design

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ Web Servers  │ Applications │ System Logs  │ Network Devices    │
│ (Apache/Nginx)│ (Custom)    │ (Syslog)    │ (Firewalls, IDS)   │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────────┘
       │              │              │                │
       ▼              ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BEATS (Log Shippers)                        │
├─────────────────────────────────────────────────────────────────┤
│  • Filebeat (log file shipping)                                 │
│  • Metricbeat (system metrics)                                  │
│  • Winlogbeat (Windows Event logs)                              │
│  • Packetbeat (network traffic)                                 │
│  • Heartbeat (uptime monitoring)                                │
└─────────────────────────────────────────────────────────────────┘
       │
       │  TCP/TLS Port 5044
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LOGSTASH (Log Processing)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT PHASE                                                  m │
│  ├─ beats input (5044): Receive from Beats                      │
│  ├─ syslog input (5140): Receive syslog messages                │
│  ├─ tcp input (5000): Raw TCP messages                          │
│  └─ file input: Direct file reading                             │
│                                                                 │
│  FILTER PHASE (Data Transformation)                             │
│  ├─ grok: Pattern matching & field extraction                   │
│  ├─ mutate: Field manipulation                                  │
│  ├─ geoip: Geographic IP enrichment                             │
│  ├─ date: Timestamp parsing                                     │
│  ├─ json: Parse JSON payloads                                   │
│  └─ drop: Remove unwanted events                                │
│                                                                 │
│  OUTPUT PHASE                                                   │
│  ├─ elasticsearch: Primary destination                          │
│  ├─ file: Backup to disk                                        │
│  └─ stdout: Debug output                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
       │
       │  HTTP/TLS Port 9200
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│              ELASTICSEARCH (Search & Storage)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLUSTER (3+ nodes for HA)                                      │
│  ├─ Master-eligible nodes: Cluster state management             │
│  ├─ Data nodes: Index storage & query execution                 │
│  ├─ Ingest nodes: Logstash alternative for processing           │
│  └─ Coordinating nodes: Request routing                         │
│                                                                 │
│  INDICES (Auto-created per day)                                 │
│  ├─ logstash-2026.05.21: Today's logs                           │
│  ├─ logstash-2026.05.20: Yesterday's logs                       │
│  └─ .alerts-*: Alert documents                                  │
│                                                                 │
│  FEATURES                                                       │
│  ├─ Inverted index: Fast full-text search                       │
│  ├─ Sharding: Parallel query execution                          │
│  ├─ Replication: High availability & durability                 │
│  └─ Aggregations: Statistical analysis                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
       │
       │  HTTP/TLS Port 9200 & 5601
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  KIBANA (Visualization)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FEATURES                                                       │
│  ├─ Discover: Ad-hoc search & filtering                         │
│  ├─ Visualize: Charts, graphs, maps                             │
│  ├─ Dashboard: Multi-visualization reports                      │
│  ├─ Canvas: Custom presentations                                │
│  ├─ Alerting: Rule creation & notifications                     │
│  └─ Machine Learning: Anomaly detection                         │
│                                                                 │
│  DASHBOARDS CREATED                                             │
│  ├─ Security Overview: Real-time threat metrics                 │
│  ├─ Threat Detection: Attack pattern dashboard                  │
│  ├─ Compliance Monitoring: PCI-DSS/HIPAA tracking               │
│  └─ Infrastructure Health: System performance                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Elasticsearch Cluster Architecture

```
CLUSTER (3 Nodes - High Availability):

Node 1 (Master + Data)              Node 2 (Master + Data)              Node 3 (Dedicated Master)
├─ Master-eligible: YES              ├─ Master-eligible: YES              ├─ Master-eligible: YES
├─ Data storage: YES                 ├─ Data storage: YES                 ├─ Data storage: NO
├─ Ingest capable: YES               ├─ Ingest capable: YES               ├─ Ingest capable: NO
├─ Shards: Primary + Replicas        ├─ Shards: Primary + Replicas        └─ Node discovery only
└─ 32GB RAM, 8 vCPU                  └─ 32GB RAM, 8 vCPU

DISCOVERY MECHANISM:
├─ Zen Discovery: Node-to-node communication
├─ Master election: Quorum-based (3 nodes = 2 quorum)
└─ Cluster state: Replicated to all nodes

DATA ORGANIZATION:

Index: logstash-2026.05.21 (Today's logs)
├─ Shard 0 (Primary)                 ├─ Shard 1 (Primary)
│  ├─ Node: 1                        │  ├─ Node: 2
│  └─ Replicas: 1 (Node 2)           │  └─ Replicas: 1 (Node 1)
│                                     │
└─ Replica placement: Cross-node for durability

RETENTION POLICY (Index Lifecycle Management):
├─ Hot (0-90 days): High performance, searchable
├─ Warm (90-365 days): Archive storage, slower search
└─ Cold (365+ days): Compliance retention, minimal access
```

### Logstash Pipeline Architecture

```
MAIN PIPELINE STRUCTURE:

logstash-main.conf
├─ INPUT SECTION
│  ├─ beats { port => 5044; ssl => true; }
│  ├─ syslog { port => 5140; }
│  └─ tcp { port => 5000; }
│
├─ FILTER SECTION
│  ├─ if [type] == "apache" { include "filters/apache.conf" }
│  ├─ if [type] == "syslog" { include "filters/syslog.conf" }
│  ├─ if [type] == "windows" { include "filters/windows.conf" }
│  ├─ if [type] == "application" { include "filters/application.conf" }
│  │
│  └─ ENRICHMENT FILTERS (All logs)
│     ├─ geoip { source => "source.ip" }
│     ├─ mutate { add_field => { "[@metadata][index]" => "logstash-%{+YYYY.MM.dd}" } }
│     └─ date { match => [ "timestamp", "ISO8601" ] }
│
└─ OUTPUT SECTION
   ├─ elasticsearch { hosts => ["localhost:9200"] }
   └─ if "_grokparsefailure" in [tags] { file { path => "/var/log/logstash/failed.log" } }

FILTER PLUGIN DETAILS:

Apache Filter (filters/apache.conf):
├─ grok pattern: COMBINEDAPACHELOG
├─ Extracts: method, path, status, bytes, user_agent
└─ Enriches: http.status_category (2xx, 3xx, 4xx, 5xx)

Syslog Filter (filters/syslog.conf):
├─ grok pattern: SYSLOGLINE
├─ Extracts: program, pid, severity, message
└─ Normalizes: syslog_level to standard severity

Windows Filter (filters/windows.conf):
├─ json { source => "message" }
├─ Extracts: event_id, computer, security_id, event_data
└─ Maps: Event ID to human-readable event type
```

---

## Data Flow Example: Apache Web Server Attack

### Scenario: SQL Injection Attack Attempt

```
1. ATTACK OCCURS (Web Server)
   ─────────────────────────────────────────────
   Time: 2026-05-21 14:23:45 UTC
   Request: GET /search.php?q=' OR '1'='1 HTTP/1.1
   Source IP: 203.0.113.42
   Response: 403 Forbidden

2. LOG ENTRY (Apache access.log)
   ─────────────────────────────────────────────
   203.0.113.42 - - [21/May/2026:14:23:45 +0000] 
   "GET /search.php?q=' OR '1'='1 HTTP/1.1" 403 456 "-" 
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

3. FILEBEAT READS LOG
   ─────────────────────────────────────────────
   Filebeat@server01 >> Logstash:5044

4. LOGSTASH PROCESSES (Grok Filter)
   ─────────────────────────────────────────────
   GROK PATTERN MATCHING:
   %{COMBINEDAPACHELOG}
   
   EXTRACTED FIELDS:
   {
     "clientip": "203.0.113.42",
     "ident": "-",
     "auth": "-",
     "timestamp": "21/May/2026:14:23:45 +0000",
     "request": "GET /search.php?q=' OR '1'='1 HTTP/1.1",
     "response": 403,
     "bytes": 456,
     "referrer": "-",
     "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
   }

5. LOGSTASH ENRICHES
   ─────────────────────────────────────────────
   GEOIP ENRICHMENT:
   {
     "geoip": {
       "ip": "203.0.113.42",
       "city_name": "Unknown",
       "country_code2": "US",
       "latitude": 37.5,
       "longitude": -97.5
     }
   }
   
   SQL INJECTION DETECTION:
   {
     "is_sql_injection": true,
     "sql_injection_keywords": ["OR", "1", "1"],
     "attack_confidence": 0.95
   }
   
   NORMALIZED FIELDS:
   {
     "http": {
       "request": {
         "method": "GET",
         "path": "/search.php",
         "query": "q=' OR '1'='1"
       },
       "response": {
         "status_code": 403,
         "status_category": "4xx_client_error"
       }
     },
     "source": {
       "ip": "203.0.113.42"
     },
     "user_agent": {
       "original": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
       "device": "Windows",
       "os": "Windows 10"
     }
   }

6. ELASTICSEARCH STORES
   ─────────────────────────────────────────────
   Index: logstash-2026.05.21
   Document Type: _doc
   
   {
     "@timestamp": "2026-05-21T14:23:45.000Z",
     "message": "[original Apache log line]",
     "http": { ... },
     "source": { ... },
     "geoip": { ... },
     "is_sql_injection": true,
     "sql_injection_keywords": ["OR", "1", "1"],
     "attack_confidence": 0.95
   }

7. ALERT RULE TRIGGERS
   ─────────────────────────────────────────────
   ALERT RULE: "SQL Injection Attack Pattern"
   
   Condition:
   - is_sql_injection: true
   - http.response.status_code: 403
   - Source IP: 203.0.113.42
   
   ALERT FIRED:
   {
     "severity": "HIGH",
     "rule": "SQL Injection Attack Detected",
     "description": "Possible SQL injection attempt from 203.0.113.42",
     "timestamp": "2026-05-21T14:23:46Z",
     "action": "ALERT - BLOCK IP"
   }

8. KIBANA DASHBOARDS UPDATE
   ─────────────────────────────────────────────
   Dashboard: Threat Detection
   ├─ Alert count: +1 (now shows 48 alerts)
   ├─ Top attack sources: 203.0.113.42 moves to #1
   ├─ Timeline: Spike shown in SQL Injection patterns
   └─ Notification: Email/Slack sent to SOC team

9. INCIDENT RESPONSE
   ─────────────────────────────────────────────
   ├─ SOC analyst reviews alert in Kibana
   ├─ Verifies attack pattern (SQL keywords confirmed)
   ├─ Checks IP reputation (possibly known attacker)
   ├─ Blocks IP via firewall rule
   ├─ Queries related events from same IP
   │  └─ Found: 24 similar attempts in last hour
   ├─ Analyzes impact:
   │  └─ All requests blocked (no database access)
   ├─ Creates incident ticket in JIRA
   └─ Documents findings in incident report
```

---

## Elasticsearch Query Examples

### Query 1: Find All SQL Injection Attempts (Last 24 Hours)

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "is_sql_injection": true
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-24h"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "by_source_ip": {
      "terms": {
        "field": "source.ip",
        "size": 10
      }
    },
    "attacks_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "interval": "1h"
      }
    }
  }
}
```

### Query 2: Brute Force Attack Detection (5+ Failed Logins from Same IP)

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "service": "sshd"
          }
        },
        {
          "term": {
            "event.outcome": "failure"
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-5m"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "by_source_ip": {
      "terms": {
        "field": "source.ip",
        "min_doc_count": 5
      },
      "aggs": {
        "unique_users": {
          "cardinality": {
            "field": "user.name"
          }
        }
      }
    }
  }
}
```

### Query 3: Data Exfiltration Detection (Large Data Transfer)

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "bytes_out": {
              "gte": 1000000000  // 1GB
            }
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-24h"
            }
          }
        }
      ],
      "filter": [
        {
          "term": {
            "direction": "outbound"
          }
        }
      ]
    }
  },
  "aggs": {
    "by_user": {
      "terms": {
        "field": "user.name",
        "size": 20
      },
      "aggs": {
        "total_bytes": {
          "sum": {
            "field": "bytes_out"
          }
        },
        "top_destinations": {
          "terms": {
            "field": "destination.ip"
          }
        }
      }
    }
  }
}
```

---

## Performance Optimization

### Index Optimization

```
DAILY INDEX ROLLOVER:
├─ Pattern: logstash-YYYY.MM.DD
├─ Size: ~50GB/day (12.5K events/sec)
├─ Refresh interval: 1 second (real-time search)
├─ Shard count: 5 (parallel queries)
└─ Replica count: 1 (high availability)

MAPPING OPTIMIZATION:
├─ Keyword fields: IP addresses, hostnames (exact match)
├─ Text fields: Message content (full-text search)
├─ Numeric fields: Bytes, response codes (aggregations)
└─ Date fields: Timestamps (range queries)

QUERY OPTIMIZATION:
├─ Filter context: Cached results (faster on repeated queries)
├─ Must clause: Scored relevance (slower, use when needed)
├─ Aggregation pruning: Limit terms aggregation to 100
└─ Scroll API: Large result sets (avoid from:size pagination)
```

---

## Security Implementation

### Authentication & Authorization

```
X-PACK SECURITY FEATURES:
├─ User authentication: Username/password, LDAP, SAML
├─ Role-based access control (RBAC)
│  ├─ superuser: Full access
│  ├─ soc_analyst: Read all indices, create alerts
│  ├─ security_admin: Manage users and roles
│  └─ viewer: Read-only access to dashboards
├─ Index-level security: Users can only see assigned indices
└─ Field-level security: Mask sensitive data (credit cards, SSNs)

ENCRYPTION:
├─ TLS in transit: Beats → Logstash → Elasticsearch → Kibana
├─ Encryption at rest: Disk encryption (LUKS) + Elasticsearch encryption
└─ API key rotation: Automated quarterly
```

---

This architecture supports enterprise-scale security operations with real-time threat detection, compliance monitoring, and rapid incident response capabilities.
