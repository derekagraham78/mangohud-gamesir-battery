# Contributing

Bug reports, hardware test results and pull requests are welcome.

For a new controller, include the exact model, USB vendor/product ID,
connection mode, Linux distribution and kernel version. Report what
`python3 bin/gamesir-battery.py --once` prints and whether the receiver has a
battery entry in `/sys/class/power_supply`.

Do not assume another GameSir device uses the same report layout. Supporting
a new ID needs a verified report ID, length, battery offset and heartbeat
behavior. Confirm that reading battery data does not disrupt controller input.
Please avoid posting raw input captures containing unrelated personal activity.

Run the tests before submitting:

```sh
python3 -m unittest discover -s tests -v
```

Keep hardware access outside MangoHud, preserve normal-user device access and
document limitations. Include tests for report parsing or reconnection changes.
