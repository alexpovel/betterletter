# Dictionaries for spell-checking

The [subdirectory](filtered) contains the same dictionaries as this base directory, but filtered to only hold words actually containing special characters of the respective languages.

So if a base dictionary contains *x* entries, but only a quarter of the word entries contain special characters, the filtered dictionaries will be much shorter.
By extension, this should make searching through them, and therefore virtually the entire program, faster by roughly the same factor.

**The filtered dictionaries are created automatically if not already present**.
They can therefore be recreated by deleting them.

## Sources

### de

- <https://sourceforge.net/projects/germandict/files/>
