# obs2anki

###### cs50x final project

###### [Video showcase](https://youtu.be/iavZXSAHzhQ)

A command-line tool to generate Anki notes from markdown tables in Obsidian

## Project details

I like to group my Chinese vocab in Obsidian using tables like so:

| Term   | Definition  |
| ------ | ----------- |
| term1  | definition1 |
| term2  | definition2 |
| ...    | ...         |

As far as I am aware, Anki note generators such as [Obsidian_to_Anki](https://github.com/ObsidianToAnki/Obsidian_to_Anki) are not able to handle tables like above. This project's goal is to solve this issue, besides a few other problems, listed below.

- If a field is not specified at all, it will be cleared in Anki on export. I don't like this behavior since I want to generate the pinyin field separately.
- There are reports of slowdown when
- I started using neovim (btw) so a command-line solution would be more flexible.

Connection to Anki is done through [anki-connect](https://git.foosoft.net/alex/anki-connect) in [`anki.py`](./anki.py). A lot of the code is based off of the Python example on anki-connect's README. One notable difference is the pattern matching in `parse_response` to elegantly distinguish errors. I am aware of packages like [`anki-connect-api`](https://pypi.org/project/anki-connect-api/) but it didn't provide much on top of the REST API so I decided to implement everything myself.

[`find.py`](./find.py) contains the logic to create a file, which is mainly the regular expression in [`config.py`](./config.py). Obsidian vaults can get quite big, so `re.finditer` over `pathlib.Path.r?glob` can be quite slow. Therefore, I used [ripgrep](https://github.com/BurntSushi/ripgrep) to find all the tables quickly before processing the data. This is done using ripgrep's `--json` argument, which converts the output to a series of JSON objects which can be parsed and pattern-matched easily.

Global tags are hard-coded in [`config.py`](./config.py), useful to distinguish generated notes in Anki. File-level tags are stored in the markdown metadata in YAML format, parsed using `PyYAML`. This breaks my original goal of only using stdlib modules, but it's somewhat unavoidable without writing a YAML parser from scratch so I let it slide. Group-level tags are part of the table regex and note-specific tags are detected via the column header.

Caching notes are handled by `NoteCache` inside [`note_cache.py`](./note_cache.py). It is essentially a wrapper around a dictionary of `(notetype, sort_key) : anki_id` pairs. This is useful for updating notes since the note ID is required to update a note's tags and/or fields. I decided to store the file in a YAML format despite its [complexity and typing pitfalls](https://stackoverflow.com/questions/65283208/toml-vs-yaml-vs-strictyaml) since it seems to be the standard for markdown-related data and I already had `PyYAML` as a dependency.

These parts are combined in [`main.py`](./main.py). It takes all the detected notes, generates a corresponding anki-connect request (`updateNote` if it exists in the cache, `addNote` otherwise). These requests are bundled into one `multi` request to avoid spamming the API. The results are then processed, reporting any errors and updating the cache as needed. The command-line interface is also in this file, created using [`argparse`](https://docs.python.org/3/library/argparse.html) to use the standard library as much as possible.

In particular, the `--verbose` option was implemented by creating a function that is either `print` or a no-op depending on the value of the flag. This can then be used anywhere for extra information that should only print with the flag enabled. This quickly falls apart as the feature is needed outside of [`main.py`](./main.py), though: the function itself is passed into the other functions to replicate this behavior. I think implementing proper logging would have been a better choice in this case.

I also exported the program as a nix flake for ease of use. With [nix](https://nix.dev/) installed, running obs2anki is a single command without any installations or dependency management (see [how to run](#how-to-run) below). It uses the `pkgs.writeShellApplication` utility to wrap a one-line script that starts Python to include ripgrep in PATH.

### Potential improvements

#### Features / options

- Ignore certain files
- Other regex patterns
- A separate config file?
- Better output formatting
- More clearly defined verbosity levels
- Deleting notes (or changing the sort key)
- Port to an Obsidian plugin

#### Performance

According to `cProfile`, ~90% (1.21s out of 1.35s on a vault with 396 files and 143 notes) of runtime is spent waiting for anki-connect. This is may be because I'm using the `multi` API call with 1 sub-request for each note found.

This could probably be improved by using `addNotes` instead of multiple `addNote` calls and/or saving all fields to the cache and only updating notes that have changed.

I might also experiment with using Anki's built-in import system to automatically update/insert all notes at once.

## How to run

Requirements:

- python3 (tested on 3.12, but should also work on 3.10)
  - [PyYAML](https://pypi.org/project/PyYAML/)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [Anki](https://ankiweb.net/) with [anki-connect](https://git.foosoft.net/alex/anki-connect) installed

### With nix flakes

Run directly with `nix run`:

```sh
$ nix run github:n0Oo0Oo0b/obs2anki -- [args]
```

Or install to an ephemeral shell:

```sh
$ nix shell github:n0Oo0Oo0b/obs2anki
$ obs2anki [args]
```

### By cloning

Clone the repo

```sh
$ git clone https://github.com/n0Oo0Oo0b/obs2anki.git
$ cd obs2anki
```

Install dependencies

```sh
$ python3 -m venv .venv && source .venv/bin/activate  # optional but recommended
$ python3 -m pip install -r requirements.txt
```

Run

```sh
$ python3 main.py [args]
```

## Usage

```
usage: main.py [-h] [-v] [-i] [-I] [-c CACHE_FILE] vault_path

positional arguments:
  vault_path            Path to Obsidian vault root.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Include detailed output, useful for debugging.
  -i, --ignore-cache    Ignore the cache file and create a new one. Recommended after deleting notes.
  -I, --no-cache        Ignore the cache file and don't create one.
  -c CACHE_FILE, --cache-file CACHE_FILE
                        Path to cache file to use, relative to vault root
```
