# specialsinserter

In a given text, replaces alternative spellings of special characters with their proper spellings.

For example, German special characters and their corresponding alternative spellings (e.g. when no proper keyboard layout is at hand, or ASCII is used) are:

| Special Character | Alternative Spelling |
| :---------------: | :------------------: |
|        Ä/ä        |        Ae/ae         |
|        Ö/ö        |        Oe/oe         |
|        Ü/ü        |        Ue/ue         |
|        ẞ/ß        |        SS/ss         |

These pairings are recorded [here](specialsinserter/language_specials.json).

Going from left to right is simple: replace all special characters with their alternative spellings, minding case.
That use case is also supported by this tool (reverse flag).

The other direction is much less straightforward: there exist countless words for which alternative spellings occur somewhere as a pattern, yet replacing them with the corresponding special character would be wrong:

| Character | Correct Spelling  | Wrong Spelling |
| --------- | ----------------- | -------------- |
| *Ä*       | **Ae**rodynamik   | Ärodynamik     |
| *Ä*       | Isr**ae**l        | Isräl          |
| *Ä*       | Schuf**ae**intrag | Schufäintrag   |
| *Ö*       | K**oe**ffizient   | Köffizient     |
| *Ö*       | Domin**oe**ffekt  | Dominöffekt    |
| *Ö*       | P**oet**          | Pöt            |
| *Ü*       | Abente**ue**r     | Abenteür       |
| *Ü*       | Ma**ue**r         | Maür           |
| *Ü*       | Ste**ue**rung     | Steürung       |
| *ß*       | Me**ss**gerät     | Meßgerät       |
| *ß*       | Me**ss**e         | Meße           |
| *ß*       | Abschlu**ss**     | Abschluß       |

just to name a few, pretty common examples.

As such, this tool is based on a dictionary lookup, see also the [containing directory](specialsinserter/dicts/).

## Examples

See also the [tests](tests/).

### de

The input:

> Ueberhaupt braeuchte es mal einen Teststring.
> Saetze ohne Bedeutung, aber mit vielen Umlauten.
> DRPFA-Angehoerige gehoeren haeufig nicht dazu.
> Bindestrich-Woerter spraechen Baende ueber Fehler.
> Doppelgaenger-Doppelgaenger sind doppelt droelfzig.
> Oder Uemlaeuten? Auslaeuten? Leute gaebe es, wuerde man meinen.
> Ueble Nachrede ist naechtens nicht erlaubt.
> Erlaube man dieses, waere es schoen uebertrieben.
> Busse muesste geloest werden, bevor Gruesse zum Gruss kommen.
> Busse sind Geraete, die womoeglich schnell fuehren.
> Voegel sind aehnlich zu Oel.
> Hierfuer ist fuer den droegen Poebel zu beachten, dass Anmassungen zu Gehoerverlust fuehren koennen.
> Stroemelschnoesseldaemel!

is turned into:

> Überhaupt bräuchte es mal einen Teststring.
> Sätze ohne Bedeutung, aber mit vielen Umlauten.
> DRPFA-Angehörige gehören häufig nicht dazu.
> Bindestrich-Wörter sprächen Bände über Fehler.
> Doppelgänger-Doppelgänger sind doppelt droelfzig.
> Oder Uemlaeuten? Auslaeuten? Leute gäbe es, würde man meinen.
> Üble Nachrede ist nächtens nicht erlaubt.
> Erlaube man dieses, wäre es schön übertrieben.
> Buße müsste gelöst werden, bevor Grüße zum Gruß kommen.
> Buße sind Geräte, die womöglich schnell führen.
> Vögel sind ähnlich zu Öl.
> Hierfür ist für den drögen Pöbel zu beachten, dass Anmaßungen zu Gehörverlust führen können.
> Stroemelschnoesseldaemel!

---

Note that some corrections are out of scope for this little script, e.g.:

> Busse

In German, *Busse* and *Buße* are two words of vastly different meaning (*busses* and *penance*, respectively).
Unfortunately, they map to the same alternative spelling of *Busse*.
The tool sees *Busse* (meaning *just that*, with no intent of changing it), notices *Buße* is a legal substitution, and therefore makes it.
The tool has no awareness of context.

Turning substitutions like these off would mean the tool would no longer emit *Buße*, ever.
This could be as undesirable as the current behaviour.
There seems to be no easy resolve.

## Running

### Prerequisites

Ideally, run the project (as is good, albeit annoying practice) in its own virtual environment.
This project uses [poetry](https://python-poetry.org/) for dependency management.
Refer to the [poetry config file](pyproject.toml) for more info (e.g. the required Python modules to install if you don't want to deal with `poetry`).

Using poetry, from the project root, run:

```bash
# Install virtual environment according to lock file
# (if available in repo),
# otherwise pyproject.toml:
poetry install
# Run command within that environment:
poetry run python -m specialsinserter -h
```

### Usage

Usage help (invoke from this project's root) will display all options:

```bash
# Naked call (alternatively, use poetry)
poetry run python -m specialsinserter -h
```

The tool can read from STDIN (outputting to STDOUT), or work with the clipboard (overwriting its contents with a corrected version).
This allows for example:

```bash
$ cat test.txt
Hoeflich fragen!
$ cat test.txt | poetry run python -m specialsinserter de
Höflich fragen!
# Reverse mode:
$ cat test.txt | poetry run python -m specialsinserter de | poetry run python -m specialsinserter -r de
Hoeflich fragen!
```

or

```bash
poetry run python -m specialsinserter -c de
# Nothing happens: clipboard is read and written to
# silently.
```

After installing (see below) the package, these calls should work system-wide.

### Run tests

The testing framework is installed as a development dependency.
This allows us, after `poetry install`, to simply run:

```bash
poetry run pytest
```

## Installation

You can install this project system-wide, using your system Python:

```bash
pip install --editable .
```

This relies on [setup.py](setup.py) (which `poetry` does not use).
An editable install (symlink) mode allows you to modify the source without having to
reinstall.

Note that this approach is discouraged, since your system Python might conflict with
the [requirements](pyproject.toml) of this project (hence, `poetry`).
However, if you installed successfully and have all requirements in place, you can call
this tool directly:

```bash
python -m specialsinserter -h
```

## AutoHotKey

This tool can be integrated with [AutoHotKey](https://www.autohotkey.com/), allowing you
to use it at the touch of a button.
This can be used to setup a keyboard shortcut to run this tool in-place, quickly replacing
what you need without leaving your text editing environment.

I was unable to use `poetry` commands for this, getting

> The system cannot find the file specified.

It works with plain `python` invocations.
Thanks to `SetWorkingDir`, we do *not* have to [install](#installation) the module
system-wide.
*However*, the requirements need to be installed and available to the plain `python`
command.

The AutoHotKey file is [here](specialsinserter.ahk).

Follow [this guide](https://www.autohotkey.com/docs/FAQ.htm#Startup) to have the script
launch on boot automatically.
