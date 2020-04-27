# CISOT Network Monitor
Service is implemented with Ryu framework.

## Features
- Link delay measurement
- Bandwidth measurement
- Packet loss rate measurement

## Launching
- Debug mode: `ryu-manager --verbose --observe-links network_monitor.py`
- Production mode: `ryu-manager --observe-links network_monitor.py`

## CLI options
| Name         | Value type  | Example               |    
|--------------|-------------|-----------------------|
| --wsapi-port | integer     | --wsapi-port=8080     |

## REST API
| Method | Url                   | Response Example                                   |
|--------|-----------------------|----------------------------------------------------|
| GET    | /networkmonitor/links | [{"src_dpid": "00:00:00:00:00:00:00:01", "plr_percents": 0.0, "bandwidth_bit_per_sec": 120.03, "delay_ms": 1.8, "dst_dpid": "00:00:00:00:00:00:00:02"}] |

## References
- Ryu framework home page is `https://osrg.github.io/ryu/`
- The link delay measurement approach is described in `https://ieeexplore.ieee.org/document/6727820`