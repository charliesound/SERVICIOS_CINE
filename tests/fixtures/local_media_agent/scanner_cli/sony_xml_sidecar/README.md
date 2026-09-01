# sony_xml_sidecar

Synthetic scanner fixture family for SOURCE_COLOR_PROFILE Sony XML sidecars.

No real media. No client data. No real F:\SIRUELA XML sidecars.

Pattern (V1): `<dir>/<clip_base>.MP4` -> `<dir>/<clip_base>M01.XML` (exact sibling).

Cases covered synthetically:
1.  s-log3-cine + s-gamut3-cine + rec709
2.  ex-cine1 + rec709
3.  s-cinetone + rec709
4.  rec709 + rec709
5.  valid XML without color fields
6.  malformed XML
7.  sidecar absent
8.  LUT absent
9.  explicit synthetic LUT metadata (record-only, never applied)
10. MP4 path + sibling M01.XML resolution
11. same basename in another directory must NOT be associated

Synthetic-only policy:
- All `.MP4` placeholders are tiny text files containing
  `SYNTHETIC_PLACEHOLDER_NOT_MEDIA` (they are not playable media).
- All `.XML` sidecars are minimal synthetic Sony-style documents.