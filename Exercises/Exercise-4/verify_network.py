"""Run inside the temporary Flask container to test Docker DNS and servers."""
import json
import socket
import subprocess

report = {}
for host, port in [('mysql', 3306), ('redis', 6379)]:
    address = socket.gethostbyname(host)
    with socket.create_connection((host, port), timeout=10) as connection:
        if host == 'mysql':
            packet = connection.recv(1024)
            assert packet[4] == 10, 'Expected MySQL protocol-10 handshake'
            details = {'protocol': packet[4], 'server_version': packet[5:].split(b'\0')[0].decode()}
        else:
            connection.sendall(b'*1\r\n$4\r\nPING\r\n')
            reply = connection.recv(1024).decode()
            assert reply == '+PONG\r\n'
            details = {'reply': reply.strip()}
    ping = subprocess.run(['ping', '-c', '3', '-W', '3', host], text=True, capture_output=True)
    assert ping.returncode == 0 and '0% packet loss' in ping.stdout
    report[host] = {'dns_address': address, 'port': port, 'tcp_connected': True,
                    'ping': ping.stdout, **details}
print(json.dumps(report))
