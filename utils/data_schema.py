NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
]

NSL_KDD_COLUMNS_WITH_DIFFICULTY = NSL_KDD_COLUMNS + ["difficulty"]

CATEGORICAL_COLUMNS = ["protocol_type", "service", "flag"]

DOS_ATTACKS = {
    "back",
    "land",
    "neptune",
    "pod",
    "smurf",
    "teardrop",
    "mailbomb",
    "apache2",
    "processtable",
    "udpstorm",
}

PROBE_ATTACKS = {
    "satan",
    "ipsweep",
    "nmap",
    "portsweep",
    "mscan",
    "saint",
}

R2L_ATTACKS = {
    "guess_passwd",
    "ftp_write",
    "imap",
    "phf",
    "multihop",
    "warezmaster",
    "warezclient",
    "spy",
    "xlock",
    "xsnoop",
    "snmpguess",
    "snmpgetattack",
    "httptunnel",
    "sendmail",
    "named",
    "worm",
}

U2R_ATTACKS = {
    "buffer_overflow",
    "loadmodule",
    "rootkit",
    "perl",
    "sqlattack",
    "xterm",
    "ps",
}


def map_attack_to_category(label):
    label_lower = str(label).strip().lower()
    if label_lower == "normal" or label_lower == "normal.":
        return "Normal"
    if label_lower in DOS_ATTACKS:
        return "DoS"
    if label_lower in PROBE_ATTACKS:
        return "Probe"
    if label_lower in R2L_ATTACKS:
        return "R2L"
    if label_lower in U2R_ATTACKS:
        return "U2R"
    return "Unknown"
