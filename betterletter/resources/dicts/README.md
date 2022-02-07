# Spell-checking dictionaries (word lists)

Dictionaries are expected to have the following properties:

- UTF-8 encoding
- entries are newline-delimited (both `CRLF` and `LF` work)
- have a corresponding language entry in [`languages.json`](../languages.json)
- no sorting required (lookup via sets)

## Sources

| Language | Source                                               | License                                                                                                  |
| :------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| de       | <https://sourceforge.net/projects/germandict/files/> | [Public Domain](https://web.archive.org/web/20220101173037/https://sourceforge.net/projects/germandict/) |
