# Snoopervisor
This tool is intended to report to Slack when a user exceeds a threshold for a certain resource.

## Config
The default config for this exists in settings.toml and is reproduced below.

* `watchers.cpu.threshold` is in percentages of a single CPU core.  For two CPU cores, 200% would be necessary.
* `watchers.memory.threshold` is in bytes.

``` ini
[users]
ignore = [
    "root",
    "systemd-resolve",
    "systemd-oom",
    "systemd-timesync",
]

[watchers.cpu]
enabled = true
threshold = 100
schedule = "*/5 * * * *"

[watchers.memory]
enabled = true
threshold = 200000000
schedule = "* * * * *"
```

### Secrets
In addition to the top config, in order for this reporter to report back to Slack, create a `.secrets.toml` file with the following content.
``` ini
[notifiers.slack]
enabled = true
channel = ""
token = ""
```