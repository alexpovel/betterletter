# Spell-checking dictionaries (word lists)

Dictionaries are expected to have the following properties:

- UTF-8 encoding
- entries are newline-delimited (both `CRLF` and `LF` work)
- have a corresponding language entry in `languages.json`
- no sorting required

## Filtering

Dictionaries could be filtered to only contain words with native characters in the first place.
However, shorter dictionaries do not do much: word lookup is, thanks to sets, *O(1)* anyway.
Memory footprint would be improved slightly, but this is a matter of only a couple Megabyte.

## Sources

| Language | Source                                               | License                                                                                                  |
| :------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| de       | <https://sourceforge.net/projects/germandict/files/> | [Public Domain](https://web.archive.org/web/20220101173037/https://sourceforge.net/projects/germandict/) |
