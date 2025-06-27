from pymodbus.client import ModbusTcpClient
import struct
import re

def extract_ascii_strings(byte_data, min_length=4):
    """
    Finds printable ASCII strings in byte array, similar to Unix 'strings' command.
    """
    ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in byte_data)
    pattern = r'[ -~]{%d,}' % min_length  # printable ASCII range
    return re.findall(pattern, ascii_str)

def scan_registers_for_ascii(ip, port, unit_id, max_registers=125, step=125):
    client = ModbusTcpClient(host=ip, port=port)
    client.connect()

    print(f" Scanning {ip} for ASCII strings in Holding Registers...")

    start = 0
    all_ascii_strings = []

    while start < max_registers:
        try:
            result = client.read_holding_registers(address=start, count=min(step, max_registers - start), unit=unit_id)

            if result.isError():
                print(f" Error reading registers {start}–{start+step-1}: {result}")
                break

            # Convert register values to bytearray
            raw_bytes = bytearray()
            for reg in result.registers:
                raw_bytes.extend(struct.pack('>H', reg))  # Big endian

            # Extract ASCII strings
            found_strings = extract_ascii_strings(raw_bytes)
            for s in found_strings:
                print(f"[Registers {start}-{start + step - 1}] 🔍 Found ASCII: '{s}'")
                all_ascii_strings.append((start, s))

        except Exception as e:
            print(f" Exception while reading at {start}: {e}")
            break

        start += step

    client.close()

    if not all_ascii_strings:
        print("No embedded ASCII strings found.")
    else:
        print(f"\nFinished. Total strings found: {len(all_ascii_strings)}")

# Example usage
scan_registers_for_ascii(
    ip='192.168.1.100',  # Replace with your target device
    port=502,
    unit_id=1,
    max_registers=1000,  # Adjust as needed (e.g., full space)
    step=125             # Max per Modbus spec
)
