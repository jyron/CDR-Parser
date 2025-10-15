from typing import Dict, Optional


def parse_cdr_line(line: str) -> Dict[str, Optional[int | str]]:
    """
    Parse a single CDR line and return normalized usage record.
    
    Args:
        line: Raw CDR line string
        
    Returns:
        Dictionary with normalized fields: id, mnc, bytes_used, dmcc, cellid, ip
    """
    line = line.strip()
    if not line:
        return None
    
    parts = line.split(',')
    if len(parts) < 2:
        return None
    
    record_id = int(parts[0])
    
    # Determine parsing scheme based on last digit of ID
    last_digit = record_id % 10
    
    if last_digit == 4:
        return parse_extended(parts)
    elif last_digit == 6:
        return parse_hex(parts)
    else:
        return parse_basic(parts)


def parse_basic(parts: list) -> Dict[str, Optional[int | str]]:
    """
    Parse basic format: <id>,<bytes_used>
    
    Args:
        parts: List of comma-separated values
        
    Returns:
        Normalized usage record
    """
    return {
        "id": int(parts[0]),
        "mnc": None,
        "bytes_used": int(parts[1]),
        "dmcc": None,
        "cellid": None,
        "ip": None
    }


def parse_extended(parts: list) -> Dict[str, Optional[int | str]]:
    """
    Parse extended format: <id>,<dmcc>,<mnc>,<bytes_used>,<cellid>
    
    Args:
        parts: List of comma-separated values
        
    Returns:
        Normalized usage record
    """
    return {
        "id": int(parts[0]),
        "mnc": int(parts[2]),
        "bytes_used": int(parts[3]),
        "dmcc": parts[1],
        "cellid": int(parts[4]),
        "ip": None
    }


def parse_hex(parts: list) -> Dict[str, Optional[int | str]]:
    """
    Parse hex format: <id>,<hex_string>
    
    The hex string is 24 characters (12 bytes):
    - Bytes 1-2 → mnc
    - Bytes 3-4 → bytes_used
    - Bytes 5-8 → cellid
    - Bytes 9-12 → ip (each byte is one IP segment)
    
    Args:
        parts: List of comma-separated values
        
    Returns:
        Normalized usage record
    """
    record_id = int(parts[0])
    hex_string = parts[1]
    
    # Extract hex bytes (each byte is 2 characters)
    mnc = int(hex_string[0:4], 16)  # Bytes 1-2
    bytes_used = int(hex_string[4:8], 16)  # Bytes 3-4
    cellid = int(hex_string[8:16], 16)  # Bytes 5-8
    
    # Parse IP address - bytes 9-12 (each byte is one IP segment)
    ip_bytes = [
        int(hex_string[16:18], 16),
        int(hex_string[18:20], 16),
        int(hex_string[20:22], 16),
        int(hex_string[22:24], 16)
    ]
    ip = '.'.join(str(b) for b in ip_bytes)
    
    return {
        "id": record_id,
        "mnc": mnc,
        "bytes_used": bytes_used,
        "dmcc": None,
        "cellid": cellid,
        "ip": ip
    }

