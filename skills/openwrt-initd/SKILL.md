---
name: openwrt-initd-service
description: Use when installing background services on OpenWrt with automatic startup on boot and process supervision. Use for agents, monitoring tools, or any long-running background processes that need persistent logging and respawn on crash.
---

# OpenWrt Init.d Service Installation

## Overview

Install background services on OpenWrt as init.d scripts with procd supervision. Services auto-start on boot, log to `/var/log/`, and respawn on failure.

## When to Use

Need to run service on OpenWrt? This skill
Is it background process? This skill
Need auto-start on boot? This skill
Need crash recovery? This skill

Use cases:
- Monitoring agents (beszel-agent, telegraf, etc.)
- Custom daemons
- Network services
- Data collectors

NOT for:
- One-time scripts (use /etc/rc.local)
- Interactive commands (run manually)
- CGIs/FastCGI (use uhttpd configuration)

## Core Pattern

OpenWrt init.d = /etc/init.d/<name> + START priority + start() function

```sh
#!/bin/sh /etc/rc.common

START=99              # Start late (network ready)
USE_PROCD=1          # Enable procd supervision

start_service() {
    procd_open_instance
    procd_set_param command "/usr/bin/service"
    procd_set_param respawn 3600 5 5
    procd_set_param stdout "/var/log/service.log"
    procd_set_param stderr "/var/log/service.log"
    procd_close_instance
}
```

## Quick Reference

| Task | Command |
|------|--------|
| Install script | cat > /etc/init.d/service-name |
| Set executable | chmod +x /etc/init.d/service-name |
| Enable autostart | /etc/init.d/service-name enable |
| Start service | /etc/init.d/service-name start |
| Check status | /etc/init.d/service-name status |
| Stop service | /etc/init.d/service-name stop |

## UCI Configuration (Optional)

For configurable services, use UCI:

```sh
# Create config
cat > /etc/config/service
config service 'main'
    option port '8080'
    option token 'abc123'

# In init.d script
local port=$(uci get service.main.port 2>/dev/null)

# Update config
uci set service.main.port='8080'
uci commit service
```

## Log Management

```sh
# Create log directory with error checking
mkdir -p /var/log || {
    echo "Error: Cannot create log directory" >&2
    return 1
}

# Set restrictive permissions
umask 077
touch "$LOG_FILE"

# Verify logs
tail -n 50 /var/log/service.log
```

## Direct Logging (When procd stdout/stderr Fails)

If procd log redirection doesn't work, use background process with redirection:

```sh
start() {
    mkdir -p /var/log /var/run || return 1

    # Stop existing
    stop

    # Start with logging
    "$PROG" \
        -l "$port" \
        -k "$ssh_key" \
        -t "$token" \
        -u "$hub_url" \
        >> "$LOG_FILE" 2>&1 &

    local pid=$!
    echo "$pid" > "$PID_FILE"
}
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Service won't start | Check shebang: #!/bin/sh /etc/rc.common |
| Enable doesn't persist | Verify symlink: ls -la /etc/rc.d/*service* |
| No logs created | Use direct redirection: >> "$LOG_FILE" 2>&1 & |
| Permissions too open | Set umask: umask 077 before touch |
| Binary not found | Copy to /usr/bin/ not /usr/local/bin |
| procd_status not found | Use pgrep or PID file instead |

## Service Script Template

```sh
#!/bin/sh /etc/rc.common

START=99
STOP=10

PROG="/usr/bin/service"
LOG_FILE="/var/log/service.log"
PID_FILE="/var/run/service.pid"

start() {
    mkdir -p /var/log /var/run || return 1

    # Read UCI config (optional)
    local setting=$(uci get service.main.setting 2>/dev/null)

    # Validate required config
    [ -z "$setting" ] && echo "Error: setting not configured" && return 1

    stop

    umask 077
    touch "$LOG_FILE"

    "$PROG" \
        --config "$setting" \
        >> "$LOG_FILE" 2>&1 &

    local pid=$!
    echo "$pid" > "$PID_FILE"
    sleep 1

    if kill -0 "$pid" 2>/dev/null; then
        echo "Service started (PID: $pid)"
        return 0
    else
        echo "Failed to start service" >&2
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") 2>/dev/null
        rm -f "$PID_FILE"
    fi
    pkill -9 -f "$PROG" 2>/dev/null
}

restart() {
    stop
    sleep 1
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "[OK] service: running (PID: $pid)"
        else
            echo "[STOPPED] service: stopped (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        local pid=$(pgrep -f "$PROG" | head -1)
        if [ -n "$pid" ]; then
            echo "[OK] service: running (PID: $pid)"
        else
            echo "[STOPPED] service: stopped"
        fi
    fi

    echo ""
    echo "=== Latest 50 log lines ==="
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 "$LOG_FILE"
    else
        echo "Log file not found: $LOG_FILE"
    fi
}
```
