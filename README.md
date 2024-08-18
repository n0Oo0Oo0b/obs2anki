# obs2anki

###### cs50x final project

A command-line tool to generate Anki notes from markdown tables in Obsidian

Requirements:

- python3 (tested on 3.12, but should also work on 3.10)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [ripgrep](https://github.com/BurntSushi/ripgrep)

## How to run

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
