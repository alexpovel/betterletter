# Spell-checking dictionaries (word lists)

Dictionaries are expected to have the following properties:

- UTF-8 encoding
- entries are newline-delimited (both `CRLF` and `LF` work)
- have a corresponding language entry in `languages.json`
- no sorting required

## Filtering

Dictionaries are filtered to only contain words containing any native characters.
If no filtered dictionary is available, a new one is created at first startup.
In the case of German, a size difference of 3 to 1 was observed.

### Rationale

Word lookup is, thanks to sets, *O(1)* : not much is gained there.
Memory footprint is improved slightly, but this is a matter of only a couple Megabyte.

However, at time of writing, the full German dictionary is around 32 MB in size, the filtered one around 11 MB.
Through profiling, a load-up (reading in the dictionary) time of roughly 0.01 seconds per MB was observed, on the currently fastest hardware class (NVMe SSD).
A 32 MB dictionary approaches a half second of load-up, which is too long.
This is the main motivation for filtering dictionaries down for usage.

## Sources

| Language | Source                                               | License                                                                                                  |
| :------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| de       | <https://sourceforge.net/projects/germandict/files/> | [Public Domain](https://web.archive.org/web/20220101173037/https://sourceforge.net/projects/germandict/) |
