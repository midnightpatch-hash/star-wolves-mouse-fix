# Patch range index

Offsets below are **file offsets**, not runtime addresses. End offsets are exclusive.
All before/after bytes are in [`patches/v1.1.0.json`](../patches/v1.1.0.json).

| ID | File range | Length | Purpose |
| --- | --- | ---: | --- |
| `text_virtual_size` | `0x230..0x234` | 4 | Increase the PE .text VirtualSize from 0x294062 to 0x2944db to cover the added code. |
| `mouse_queue_01` | `0x23181..0x23185` | 4 | Mouse DirectInput buffer: 64 to 128 records |
| `mouse_queue_04` | `0x23912..0x23916` | 4 | Expand local frame for 128 records |
| `mouse_queue_05` | `0x2391b..0x2391f` | 4 | Keep caller argument address after frame expansion |
| `mouse_queue_06` | `0x23934..0x23938` | 4 | Expand local frame for 128 records |
| `mouse_queue_07` | `0x23976..0x2397a` | 4 | Expand local frame for 128 records |
| `mouse_queue_02` | `0x239a2..0x239a6` | 4 | Mouse read request: 64 to 128 records |
| `mouse_queue_03` | `0x239b4..0x239b5` | 1 | Accept nonnegative HRESULT, including DI_BUFFEROVERFLOW |
| `mouse_queue_08` | `0x239e2..0x239e6` | 4 | Expand local frame for 128 records |
| `mouse_queue_09` | `0x23a13..0x23a17` | 4 | Keep caller argument address after frame expansion |
| `mouse_queue_10` | `0x23fa9..0x23fad` | 4 | Expand local frame for 128 records |
| `mouse_queue_11` | `0x2410c..0x24110` | 4 | Expand local frame for 128 records |
| `mouse_queue_12` | `0x2416a..0x2416e` | 4 | Expand local frame for 128 records |
| `mouse_queue_13` | `0x24221..0x24225` | 4 | Expand local frame for 128 records |
| `mouse_queue_14` | `0x24235..0x24239` | 4 | Expand local frame for 128 records |
| `sensitivity_fix_840f0` | `0x840f0..0x840f5` | 5 | Route the sensitivity bar to the 20-segment renderer; retain original rendering for other bars. |
| `cursor_hook` | `0x8e855..0x8e85a` | 5 | Redirect render-update call to the register/flags-preserving cursor preview wrapper. |
| `startup_hook` | `0x90ff3..0x90ff8` | 5 | Route the main-window background-brush setup to the black-brush fragment. |
| `sensitivity_fix_101b90` | `0x101b90..0x101b96` | 6 | Redirect sensitivity increase handler. |
| `sensitivity_fix_101c70` | `0x101c70..0x101c76` | 6 | Redirect sensitivity decrease handler. |
| `sensitivity_fix_10321d` | `0x10321d..0x103221` | 4 | Change reset/default sensitivity constant from 3.0 to 1.0. |
| `sensitivity_fix_1034eb` | `0x1034eb..0x1034f0` | 5 | Normalize saved sensitivity and obtain the 1..20 display index on menu open. |
| `sensitivity_fix_103505` | `0x103505..0x10350b` | 6 | Configure the sensitivity bar on menu open. |
| `sensitivity_fix_1045e8` | `0x1045e8..0x1045ed` | 5 | Convert reset sensitivity into a display index. |
| `sensitivity_fix_1045fe` | `0x1045fe..0x104604` | 6 | Configure the sensitivity bar on reset. |
| `resolution_filter` | `0x104755..0x1047db` | 134 | Keep seven supported 32-bit resolutions. |
| `resolution_depth_skip` | `0x1047fc..0x1047fe` | 2 | Route rejected pixel depths through the original mode-advance path; avoids the earlier settings crash. |
| `cursor_preview` | `0x295070..0x295227` | 439 | Preview buffered relative movement with DIGDD_PEEK without consuming events. |
| `sensitivity` | `0x295230..0x2954c0` | 656 | Implement 20-step sensitivity, normalization, live update and the 20-segment indicator. |
| `startup_background` | `0x2954d0..0x2954db` | 11 | Retain the original stack store and use BLACK_BRUSH (4) instead of WHITE_BRUSH (0). |
| `sensitivity_fix_34f2b8` | `0x34f2b8..0x34f2ba` | 2 | Disable an obsolete HIGHLOW relocation for an absolute operand replaced by a relative hook. |
| `sensitivity_fix_34f2d8` | `0x34f2d8..0x34f2da` | 2 | Disable the second obsolete HIGHLOW relocation for the replaced absolute operand. |
