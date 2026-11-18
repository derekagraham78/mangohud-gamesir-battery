# Protocol notes

The supported receiver is GameSir USB vendor `0x3537`, product `0x10c6`, in
XInput mode. HIDAPI can enumerate several usages for a single hidraw node, so
the reader deduplicates device paths before opening them.

The reporting heartbeat is 64 bytes: `0x0f, 0xf2`, followed by 62 zero bytes.
The reader sends it every 500 ms. This is a volatile reporting request, not
a persistent configuration write.

Enhanced input reports have ID `0x12` and length 64. Offsets include the report
ID at byte zero:

| Offset | Meaning |
| --- | --- |
| 0 | Report ID `0x12` |
| 1–4 | Stick values |
| 35 bit 0 | Charging flag, not yet hardware-validated |
| 36 | Battery percentage, 0–100 |

Short, unrelated, empty and out-of-range reports are ignored. Five seconds
without a valid report triggers reconnection. A zero battery percentage is
valid if the rest of the report is populated.

The initial G7 Pro 8K PC tests on CachyOS read 100% and later 99%, while the
controller continued to use `xpad`. The background reader refreshed its cache
and wrote `Disconnected` on SIGTERM. These observations do not establish the
accuracy of a full discharge curve or the charging flag.

Reference: [GameSir Linux tools](https://github.com/broroeror/gamesir-linux-tools),
particularly the enhanced-report parser. Additional controllers must be
verified on hardware before adding their product IDs.
