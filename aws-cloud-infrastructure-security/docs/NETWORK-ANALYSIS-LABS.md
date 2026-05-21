# Network Analysis & Wireshark Case Study

## Overview

This portfolio project demonstrates practical network security analysis skills through real-world packet capture analysis, threat detection, and security recommendations.

## Lab 1: TCP/IP Communication Analysis

### Objective
Analyze TCP three-way handshake and HTTP protocol interactions

### Tools Used
- **Wireshark**: Network protocol analyzer
- **Tcpdump**: Command-line packet capture
- **tshark**: Wireshark command-line interface

### Key Findings

#### TCP Handshake Analysis

```
Frame 1: Client → Server (SYN)
  ├─ TCP Flags: [SYN]
  ├─ Sequence Number: 0
  └─ Window Size: 65535 bytes

Frame 2: Server → Client (SYN-ACK)
  ├─ TCP Flags: [SYN, ACK]
  ├─ Sequence Number: 0
  ├─ Acknowledgment Number: 1
  └─ Window Size: 32768 bytes

Frame 3: Client → Server (ACK)
  ├─ TCP Flags: [ACK]
  ├─ Acknowledgment Number: 1
  └─ Sequence Number: 1
```

#### HTTP Protocol Inspection

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Connection: keep-alive
Accept-Encoding: gzip, deflate

HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Set-Cookie: session=abc123; Path=/
```

### Security Observations

- **HTTPS Usage**: All traffic encrypted (TLS 1.2)  
- **Security Headers**: HSTS, X-Frame-Options set  
- **Cookie Security**: Missing HttpOnly flag  
- **Compression**: Enabled (CRIME attack risk)  

### Recommendations

1. Add `HttpOnly` flag to session cookies
2. Disable HTTP compression for sensitive data
3. Implement HSTS header
4. Use secure cookie flag

---

## Lab 2: Malware Detection (DoS Attack Simulation)

### Objective
Identify and analyze Distributed Denial of Service (DDoS) attack patterns

### Attack Scenario

**Attacker**: 192.168.100.0/24 (botnet)  
**Target**: 10.0.1.100 (web server)  
**Attack Type**: SYN flood  
**Duration**: 60 seconds  

### Packet Analysis

```
Wireshark Filter: ip.src == 192.168.100.10 && tcp.flags.syn == 1

Frame 1: 192.168.100.10:60000 → 10.0.1.100:80 [SYN]
  ├─ Time: 00:00:01
  └─ Sequence: Random

Frame 2: 192.168.100.11:60001 → 10.0.1.100:80 [SYN]
  ├─ Time: 00:00:01
  └─ Sequence: Random

Frame 3: 192.168.100.12:60002 → 10.0.1.100:80 [SYN]
  ├─ Time: 00:00:01
  └─ Sequence: Random

... (thousands of identical frames)
```

### Attack Characteristics

| Metric | Value | Significance |
|--------|-------|--------------|
| Packet Rate | 10K+ pps | Abnormal (normal: 100 pps) |
| Source IPs | 254 unique | Distributed attack |
| Source Ports | Random | Botnet signature |
| Flags | SYN only | Incomplete handshakes |
| TTL | Varied | Different geographies |

### Detection Strategy

```
Wireshark Display Filter:
  tcp.flags.syn == 1 && tcp.flags.ack == 0 && 
  ip.src != 10.0.1.1 && 
  frame.time_delta < 0.001

Alert Threshold:
  > 1000 SYN packets/second = CRITICAL
  > 500 SYN packets/second = HIGH
```

### Defense Mechanisms

1. **SYN Cookies**: Prevent SYN flood connection queue exhaustion
2. **Rate Limiting**: Limit SYN packets per source IP
3. **Firewall Rules**: Block malicious source ranges
4. **Load Balancer**: Absorb attack traffic
5. **ISP DDoS Mitigation**: Upstream filtering

### Findings

- **Attack Detected**: SYN flood from 192.168.100.0/24
- **Impact**: Web server TCP connection queue exhausted
- **Legitimate Traffic**: Dropped (9 out of 10 requests)
- **Attack Duration**: 60 seconds
- **Total Packets**: 600,000+ malicious packets

### Security Recommendations

1. Deploy AWS Shield/WAF
2. Implement geographic filtering
3. Set up rate-based firewall rules
4. Monitor for SYN flood patterns
5. Establish incident response procedure

---

## Lab 3: Reconnaissance & Network Discovery

### Objective
Analyze network scanning and reconnaissance traffic

### Tools Identified

**NMAP Scan** (Network Mapper):
```
nmap -sV -p- 10.0.1.0/24

Traffic Characteristics:
├─ TCP SYN scan (port discovery)
├─ Service version detection
├─ OS fingerprinting
└─ Timing profile: "aggressive"
```

### Traffic Analysis

```
Source IP: 192.168.100.50
Target: 10.0.1.0/24 (256 hosts)

Wireshark Results:
├─ Total packets: 2,048
├─ Unique target IPs: 256
├─ Ports scanned: 1,000 per host
├─ Duration: 120 seconds
├─ Scan rate: 17 packets/second
```

### Detected Services

```
Host 10.0.1.10:
├─ 22/tcp   → SSH (OpenSSH 7.4)
├─ 80/tcp   → HTTP (Apache 2.4.6)
├─ 443/tcp  → HTTPS (Apache 2.4.6)
├─ 3306/tcp → MySQL (5.7.20)
└─ 5432/tcp → PostgreSQL (9.6.5)

Host 10.0.1.11:
├─ 22/tcp   → SSH (OpenSSH 8.2)
├─ 80/tcp   → HTTP (Nginx 1.14.0)
└─ 443/tcp  → HTTPS (Nginx 1.14.0)
```

### Security Implications

**Findings**:
- Unnecesary services exposed (MySQL, PostgreSQL)
- Multiple database services on same host
- Different SSH versions (security inconsistency)
- HTTP on port 80 (insecure)

**Risk Assessment**: HIGH
- Attackers discovered internal IP range
- Multiple exploitable services identified
- Outdated software versions detected

### Recommendations

1. **Port Hardening**:
   - Close database ports to external traffic
   - Limit SSH to bastion host only
   - Allow HTTP/HTTPS from ALB only

2. **Service Hardening**:
   - Update SSH to version 8.2+
   - Implement Web Application Firewall (WAF)
   - Disable unnecessary services

3. **Detection**:
   - IDS/IPS to detect port scans
   - Alert on multiple failed connection attempts
   - Implement port knocker/single packet auth

4. **Response**:
   - Block source IP (192.168.100.50)
   - Engage incident response team
   - Conduct network segmentation audit

---

## Lab 4: Encrypted Traffic Analysis (HTTPS/TLS)

### Objective
Analyze TLS handshake and encrypted HTTPS traffic

### TLS Handshake Capture

```
Frame 1: Client Hello
  ├─ Supported TLS Versions: 1.2, 1.3
  ├─ Cipher Suites: 15 supported
  ├─ Extensions:
  │  ├─ server_name: example.com
  │  ├─ supported_groups: x25519, secp256r1
  │  ├─ signature_algorithms: RSA-SHA256, ECDSA-SHA256
  │  └─ supported_versions: TLS 1.2, 1.3
  └─ Random: [32 bytes]

Frame 2: Server Hello
  ├─ TLS Version: 1.3
  ├─ Cipher Suite: TLS_AES_256_GCM_SHA384
  ├─ Key Share: x25519 (32 bytes)
  └─ Random: [32 bytes]

Frame 3-5: Certificate Chain + Key Exchange

Frame 6: Finished (encrypted)
  ├─ MAC: [32 bytes]
  └─ Plaintext: [encrypted]
```

### Security Analysis

**Strong Points**:
- TLS 1.3 negotiated (latest version)  
- Strong cipher: AES-256-GCM  
- Perfect Forward Secrecy (ephemeral keys)  
- Certificate chain valid  

**Weaknesses**:
- No OCSP stapling  
- No client certificate  
- Certificate valid but recently issued  

### Certificate Analysis

```
Subject: CN=www.example.com
Issuer: CN=Let's Encrypt Authority X3
Serial: 0x12345678
Valid From: 2024-01-01
Valid To: 2025-01-01
Key Size: RSA 2048-bit
Signature Algorithm: SHA256withRSA

Extensions:
├─ Subject Alt Names: *.example.com
├─ Key Usage: Digital Signature, Key Encipherment
├─ Extended Key Usage: Server Authentication
└─ Certificate Transparency: Present
```

### Data Inspection Limitations

**Limitation**: HTTPS encryption prevents payload inspection

```
Wireshark View:
├─ Client Request: [Encrypted Data]
├─ Server Response: [Encrypted Data]
├─ Size: 1234 bytes
└─ TLS Record Type: Application Data
```

**Workaround Methods**:
1. TLS termination at proxy (decrypt & inspect)
2. Application logging
3. DPI (Deep Packet Inspection) with HSM
4. Network TAP with MITM (testing only)

### Recommendations

1. Deploy WAF at TLS termination point
2. Implement OCSP stapling
3. Use TLS 1.3 exclusively (disable 1.2 long-term)
4. Monitor certificate expiration
5. Implement HPKP (HTTP Public Key Pinning)

---

## Summary & Key Learnings

### Technical Skills Demonstrated

- **Protocol Analysis**: TCP/IP, HTTP, HTTPS, TLS  
- **Threat Detection**: DoS/DDoS patterns, reconnaissance  
- **Encryption**: TLS handshake, cipher analysis  
- **Tools Mastery**: Wireshark, tcpdump, tshark  
- **Security Assessment**: Vulnerability identification  

### Security Mindset

- Understand normal vs. abnormal traffic  
- Recognize attack signatures  
- Recommend defense-in-depth solutions  
- Balance security with usability  

### Real-World Application

These skills apply to:
- **Incident Response**: Analyze security breaches
- **Threat Hunting**: Proactive threat detection
- **Compliance Audit**: Verify security controls
- **Network Engineering**: Optimize security/performance
- **Forensics**: Evidence collection and analysis

---

**Lab Version**: 2.0  
**Last Updated**: May 2026  
**Skill Level**: Intermediate/Advanced
