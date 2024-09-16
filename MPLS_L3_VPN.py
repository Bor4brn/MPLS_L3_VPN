import requests
import json

url = "http://192.168.0.32:8080/jsonrpc"

# Login
payload = {
    "jsonrpc": "2.0", "id": 1, "method": "Login",
    "params": {
        "user": "admin",
        "passwd": "admin"
    }
}

authenticate = requests.post(url, json=payload, verify=False)
cookies_string = authenticate.cookies
print(f"Cookies: {cookies_string}")

# Read/Write Transaction
payload = {
    "jsonrpc": "2.0", "id": 3, "method": "new_trans",
    "params": {
        "db": "running",
        "mode": "read_write",
        "conf_mode": "private",
        "tag": "webui-one"
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
response = req.text
th_id = json.loads(response)["result"]["th"]
print(f"Transaction: {th_id}")

# L3VPN Create
payload = {
    "jsonrpc": "2.0", "id": 4, "method": "create",
    "params": {
        "th": th_id,
        "path": "/l3vpn:vpn/l3vpn{volvo}"
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
print(f"L3VPN Create Response: {req.text}")

# Loading L3vpn
payload = {
    "jsonrpc": "2.0", "id": 5, "method": "load",
    "params": {
        "th": th_id,
        "path": "/l3vpn:vpn/l3vpn{volvo}",
        "data": {"as-number": "65101"},
        "format": "json"
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
print(f"AS Number Load Response: {req.text}")

# 1. Endpoint Load
payload = {
    "jsonrpc": "2.0", "id": 10, "method": "load",
    "params": {
        "th": th_id,
        "path": "/l3vpn:vpn/l3vpn{volvo}",
        "data": {
            "l3vpn:endpoint": [
                {
                    "id": "ep1",
                    "ce-device": "ce0",
                    "ce-interface": "GigabitEthernet0/11",
                    "ip-network": "10.10.1.0/24",
                    "bandwidth": "12000000"
                }
            ]
        },
        "format": "json",
        "mode": "create"
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
print(f"First Endpoint Load Response: {req.text}")


# QoS Policy Leafref
payload = {
    "jsonrpc": "2.0", "id": 139, "method": "get_leafref_values",
    "params": {
        "th": th_id,
        "path": "/l3vpn:vpn/l3vpn{volvo}/qos/qos-policy",
        "skip_grouping": True,
        "limit": 21
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
response = req.json()
qos_policies = response.get('result', {}).get('values', [])
print(f"QoS Policies: {qos_policies}")

# Set QoS Policy
if "GOLD" in qos_policies:
    payload = {
        "jsonrpc": "2.0", "id": 140, "method": "set_value",
        "params": {
            "th": th_id,
            "path": "/l3vpn:vpn/l3vpn{volvo}/qos/qos-policy",
            "value": "GOLD"
        }
    }
    req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
    print(f"QoS Policy Set Response: {req.text}")


# Validate Commit
payload = {
    "jsonrpc": "2.0", "id": 6, "method": "validate_commit",
    "params": {
        "th": th_id
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
response = req.text
print(f"Validate Commit Response: {response}")

# Commit Changes
payload = {
    "jsonrpc": "2.0", "id": 7, "method": "commit",
    "params": {
        "th": th_id,
        "rollback-id": True
    }
}

req = requests.post(url, cookies=cookies_string, json=payload, verify=False)
response = req.text
print(f"Commit Response: {response}")
