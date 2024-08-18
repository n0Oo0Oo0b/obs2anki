"""
Functions for interfacing with anki-connect
"""

import json
import urllib.request

# Based on anki-connect docs (https://git.foosoft.net/alex/anki-connect#python)


class AnkiConnectError(Exception):
    pass


def generate_payload(action, **params):
    return {"action": action, "params": params, "version": 6}


def authenticate():
    try:
        permission = send_request("requestPermission")
    except urllib.error.URLError:
        raise AnkiConnectError("Could not connect to Anki. Is anki-connect running?")
    if permission["permission"] != "granted":
        raise AnkiConnectError("Failed to authenticate with Anki")


def send_request(action, **params):
    payload = generate_payload(action, **params)
    req = urllib.request.Request(
        "http://127.0.0.1:8765",
        json.dumps(payload).encode("utf-8"),
    )
    resp = urllib.request.urlopen(req)
    resp_json = json.load(resp)
    return parse_response(resp_json)


def parse_response(resp):
    match resp:
        case {"result": result, "error": None}:
            return result
        case {"error": err}:
            raise AnkiConnectError(err)
        case _:
            raise AnkiConnectError("Invalid response")


def add_or_update_notes(notes):
    print(notes[0])
    can_add_notes = send_request("canAddNotesWithErrorDetail", notes=notes)
    ok = []
    duplicate = []
    for note, can_add in zip(notes, can_add_notes):
        if can_add["canAdd"]:
            ok.append(note)
            continue
        elif "empty" in can_add["error"]:
            print("Note is empty:", note)
            continue
        assert "duplicate" in can_add["error"]
        duplicate.append(note)
