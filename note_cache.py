"""
Manages notes using a JSON cache for IDs
"""

import yaml
from config import GLOBAL_TAGS
import anki


class NoteCollection:
    def __init__(self):
        self.cache = {}

    @classmethod
    def from_file(cls, filepath):
        instance = cls()
        with open(filepath) as f:
            data = yaml.safe_load(f)
        for note in data:
            instance.cache[note["model"], note["sort_field"]] = note["id"]
        return instance

    @classmethod
    def from_anki(cls):
        instance = cls()

        query = " AND ".join(f"tag:{tag}" for tag in GLOBAL_TAGS)
        note_ids = anki.send_request("findNotes", query=query)
        notes = anki.send_request("notesInfo", notes=note_ids)

        for note in notes:
            # Assume sort field is first
            sort_field = next(
                field["value"]
                for field in note["fields"].values()
                if field["order"] == 0
            )
            instance.cache[note["modelName"], sort_field] = note["noteId"]
        return instance

    def save_to(self, filepath):
        data = [
            {"model": model, "sort_field": field, "id": id_}
            for (model, field), id_ in self.cache.items()
        ]
        with open(filepath, "w") as f:
            yaml.dump(data, f)

    def __len__(self):
        return len(self.cache)

    def __getitem__(self, key):
        return self.cache.get(key)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __iter__(self):
        return iter(self.cache)

    def __repr__(self):
        return f"NoteCache(<{len(self.cache)} items>)"

    def __contains__(self, item):
        return item in self.cache
