# Windows CI timeout hardening

Added a 45-minute job timeout and explicit time limits for packaged GUI smoke (5 min), installer smoke (10 min), and upgrade/preservation smoke (12 min). This prevents a stalled GUI or installer from consuming an unbounded Windows runner. These are CI safety limits, not a fix to the original Slimer pixel-loss bug.

Windows runner has not been executed in this environment.
