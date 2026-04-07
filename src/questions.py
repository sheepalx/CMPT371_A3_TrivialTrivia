from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: int
    text: str
    options: list[str]  # always 4 options
    answer_index: int  # 0..3


QUESTIONS: list[Question] = [
    Question(
        id=1,
        text="Which protocol is connection-oriented?",
        options=["UDP", "TCP", "ICMP", "ARP"],
        answer_index=1,
    ),
    Question(
        id=2,
        text="What does DNS primarily do?",
        options=[
            "Encrypt packets",
            "Assign MAC addresses",
            "Translate domain names to IP addresses",
            "Route traffic between subnets",
        ],
        answer_index=2,
    ),
    Question(
        id=3,
        text="Which port is commonly used for HTTP (not HTTPS)?",
        options=["21", "53", "80", "443"],
        answer_index=2,
    ),
    Question(
        id=4,
        text="In the OSI model, IP operates at which layer?",
        options=["Physical", "Data Link", "Network", "Transport"],
        answer_index=2,
    ),
    Question(
        id=5,
        text="What does a 3-way handshake establish?",
        options=["DNS resolution", "TCP connection", "TLS encryption", "NAT mapping"],
        answer_index=1,
    ),
    Question(
        id=6,
        text="Which address is used to deliver frames on a LAN?",
        options=["IP address", "MAC address", "Port number", "Hostname"],
        answer_index=1,
    ),
    Question(
        id=7,
        text="Which is NOT a private IPv4 range?",
        options=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "11.0.0.0/8"],
        answer_index=3,
    ),
    Question(
        id=8,
        text="What does NAT do in most home networks?",
        options=[
            "Converts private IPs to a public IP",
            "Authenticates Wi‑Fi clients",
            "Detects packet loss",
            "Creates TCP sockets",
        ],
        answer_index=0,
    ),
    Question(
        id=9,
        text="Which command is commonly used to test reachability using ICMP?",
        options=["ping", "ssh", "nslookup", "ftp"],
        answer_index=0,
    ),
    Question(
        id=10,
        text="What is the default maximum value of a TCP/UDP port number?",
        options=["1023", "4096", "65535", "99999"],
        answer_index=2,
    ),
]

