#!/usr/bin/env python3
"""Sample automation script for trigger_automation_script()."""

from datetime import datetime


def main() -> None:
    print(f"[hello_automation] ran at {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
