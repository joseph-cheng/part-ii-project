from note import Note
from piece import Piece, Part, Measure
import xml.etree.ElementTree as ET


def parse_mxml(filename):
    """
    Takes in a filename and a Piece object with the information parsed
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    if root.tag == "score-timewise":
        print("Parsing of timewise scores is not supported. Aborting")
        return None

    # we ignore part-list because we don't care about the metadata in there

    part_nodes = get_child(root, "part")

    parsed_parts = [parse_part(part) for part in part_nodes]
    return from_parts(parsed_parts)


def parse_part(part_node):
    part = Part()
    for measure in get_child(part_node, "measure"):



def parse_measure(measure_node, tie=None, previous_divisions=None):
    """
    Parses a MusicXML measure node.

    measure_node: ET node of a measure
    tie: optionally a Note from the previous measure, if that note was tied

    returns: a (Measure, Note) tuple of the parsed measure, and optionally the last note in the measure, if it was tied
    """
    needed_nodes = get_child(
        measure_node, ["attributes", "direction", "note", "forward", "backup"])

    key = 0
    tempo = 120

    # progress through the measure for each voice
    # if no explicit voice, default to 1
    voice_progress = {1: 0}

    for node in needed_nodes:
        if node.tag == "attributes":
            key_node = next(get_child(node, "key"))
            fifths_node = next(get_child(key_node, "fifths"))
            key = int(fifths_node.text)
        elif node.tag == "direction":
            sound_node = next(get_child(node, "sound"))
            if sound_node != None:
                if "tempo" in sound_node.attributes:
                    tempo = sound_node.attributes["tempo"]
        elif node.tag == "forward":
            duration_node = next(get_child(node, "duration"))
            voice_progress = {
                voice: voice_progress[voice] + int(duration_node.text) for voice in voice_progress}
        elif node.tag == "backup":
            duration_node = next(get_child(node, "duration"))
            voice_progress = {
                voice: voice_progress[voice] - int(duration_node.text) for voice in voice_progress}
        elif node.tag == "note":
            note = parse_note(node, voice_progress, tie=tie)
            if note.tied:
                tie = note


def parse_note(note_node, voice_progress, tie=None):
    """
    parses a MusicXML note into a Note object

    note_node: node to parse
    voice_progress: dictionary mapping voices to distance through measure, in divisions
    """


def get_child(node, child_name):
    """
    Generator that gets all children of a node based on the child name

    child_name: the name of the children to find, or a list of names
    """

    def membership_checker(name): return name == child_name

    if isinstance(child_name, list):
        def membership_checker(name): return name in child_name

    for child in node:
        if membership_checker(child.tag):
            yield child
