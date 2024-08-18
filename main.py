from argparse import ArgumentParser
from pathlib import Path

from note_cache import NoteCollection
import find
import anki


def main():
    args = parse_args()

    verbose_print = print if args.verbose else lambda *_a, **_k: None
    vault_dir = args.vault_path
    cache_dir = vault_dir / args.cache_file

    try:
        anki.authenticate()
    except anki.AnkiConnectError as e:
        print(e)
        return

    # Generate note cache
    if args.ignore_cache or args.no_cache:
        cache = NoteCollection.from_anki()
        verbose_print(f"Loaded {len(cache)} notes from Anki")
    elif not cache_dir.exists():
        print(
            f"Could not find cache at {cache_dir}\n"
            "Rerun with `-i` to generate one from Anki"
        )
        return
    else:
        cache = NoteCollection.from_file(cache_dir)
        verbose_print(f"Loaded {len(cache)} notes from {cache_dir}")

    # Create request payloads
    requests = []
    keys = {}  # dict to preserve order
    for note in find.find_notes(vault_dir, verbose_print):
        cache_key = note["modelName"], next(iter(note["fields"].values()))
        verbose_print(f"  note: {cache_key}", end="")
        if id_ := cache[cache_key]:
            verbose_print(f" with ID {id_}")
            payload = anki.generate_payload(
                "updateNote",
                note={"id": id_, **note},
            )
        else:
            verbose_print(" (not found in cache)")
            payload = anki.generate_payload(
                "addNote",
                note=note,
            )
        if cache_key in keys:
            print(f"Warning: duplicate note found in vault: {cache_key}")
        keys[cache_key] = None
        requests.append(payload)

    # Send requests as batch
    print(f"{len(requests)} notes found, sending requests...")
    responses = anki.send_request("multi", actions=requests)
    print("Done!")

    # Results
    had_error = False
    new_count = 0
    modified_count = 0
    for req, resp, cache_key in zip(requests, responses, keys):
        try:
            resp = anki.parse_response(resp)
        except anki.AnkiConnectError as e:
            print(f"Error: '{e}' on note {cache_key}")
            had_error = True
            continue
        if resp:
            verbose_print(f"Setting note ID of '{cache_key}' to {resp}")
            cache[cache_key] = resp
            new_count += 1
        else:
            modified_count += 1
    print(f"{new_count} notes created, {modified_count} notes modified/unchanged")

    # Save cache to file
    if not args.no_cache:
        if had_error:
            print("Re-syncing cache file due to errors")
            cache = NoteCollection.from_anki()
        verbose_print(f"Saving cache with {len(cache)} entries to {cache_dir}")
        cache.save_to(cache_dir)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault root.",
        type=Path,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Include detailed output, useful for debugging.",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--ignore-cache",
        help="Ignore the cache file and create a new one. "
        "Recommended after deleting notes.",
        action="store_true",
    )
    parser.add_argument(
        "-I",
        "--no-cache",
        help="Ignore the cache file and don't create one.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--cache-file",
        help="Path to cache file to use, relative to vault root",
        default="ankicache.yml",
        type=Path,
    )

    return parser.parse_args()


if __name__ == "__main__":
    # import cProfile
    #
    # cProfile.run("main()")

    main()
