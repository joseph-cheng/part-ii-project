from note import Note
from piece import Piece, Part, Measure
import xml.etree.ElementTree as ET

GRACE_LENGTH = 0.3

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
    piece = Piece.from_parts(parsed_parts)
    piece.sort()
    return piece


def parse_part(part_node):
    """
    Parses a part node into a Part object

    part_node: ET node corresponding to a part

    returns: a Part object representing the parsed part node
    """
    part = Part()
    last_measure = None
    # treating ties a bit like  stack, documentation is not clear on how to handle them
    open_ties = []
    for measure in get_child(part_node, "measure"):
        part.add_measure(parse_measure(measure, previous_measure=last_measure))
        last_measure = part.get_last_measure()

    return part

def parse_measure(measure_node, open_ties=[], previous_measure=None):
    """
    Parses a MusicXML measure node.

    measure_node: ET node of a measure
    open_ties: optionally, a list of the notes that have ties that need to be closed
    previous_measure: optionally, the previous measure that was parsed

    returns: a Measure of the parsed measure
    """
    metadata_nodes = get_child(measure_node, ["attributes", "direction"])
    progress_nodes = get_child(measure_node, ["note", "forward", "backup"])

    key = 0
    tempo = 120
    divisions = None
    length = None
    onset = 0
    if previous_measure != None:
        divisions = previous_measure.divisions
        length = previous_measure.length
        tempo = previous_measure.tempo
        onset = previous_measure.onset + previous_measure.length

       # progress through the measure for each voice
    voice_progress = {0: 0}

    for node in metadata_nodes:
        if node.tag == "direction":
            sound_node = next(
                get_child(node, "sound"), None)
            if sound_node != None:
                if "tempo" in sound_node.attrib:
                    tempo = int(sound_node.attrib["tempo"])
        elif node.tag == "attributes":
            divisions_node = next(get_child(node, "divisions"), None)
            if divisions_node != None:
                divisions = int(divisions_node.text)
            time_node = next(get_child(node, "time"), None)
            if time_node != None:
                beats_node = next(get_child(time_node, "beats"))
                beat_type_node = next(get_child(time_node, "beat-type"))
                # TODO: support for compound time signatures maybe?
                length = (4 / (int(beat_type_node.text))) * \
                    int(beats_node.text)

    measure = Measure(length, divisions, tempo, onset)

    for node in progress_nodes:
        if node.tag == "forward":
            duration_node = next(
                get_child(node, "duration"))
            voice_progress = {
                voice: voice_progress[voice] + int(duration_node.text) for voice in voice_progress}
        elif node.tag == "backup":
            duration_node = next(
                get_child(node, "duration"))
            voice_progress = {
                voice: voice_progress[voice] - int(duration_node.text) for voice in voice_progress}
        elif node.tag == "note":
            note = parse_note(node, voice_progress, measure)
            # if not rest
            if note != None:
                if note.tie_type == Note.TieType.STOP:
                    note.tied_from = open_ties.pop()
                elif note.tie_type == Note.TieType.MIDDLE:
                    note.tied_from = open_ties.pop()
                    open_ties.append(note)
                elif note.tie_type == Note.TieType.START:
                    open_ties.append(note)

            measure.add_note(note)

    return measure


def parse_note(note_node, voice_progress, current_measure):
    """
    parses a MusicXML note into a Note object

    note_node: node to parse
    voice_progress: dictionary mapping voices to distance through measure, in divisions
    current_measure: current measure that is being processed. Needed for getting notes in a chord
    """

    note_value = None
    duration = None
    voice = 0
    grace = False
    chorded_with = None
    tie_type = Note.TieType.NONE
    rest = False

    alter_dict = {0: '', 1: '#',
                  2: 'x', -1: 'b', -2: 'bb'}

    for child in note_node:
        if child.tag == "grace":
            duration = GRACE_LENGTH
            grace = True
        elif child.tag == "chord":
            chorded_with = current_measure.get_last_added_note()
        elif child.tag == "pitch":
            note = None
            alter = 0
            octave = None
            for pitch_child in child:
                if pitch_child.tag == "step":
                    note = pitch_child.text
                elif pitch_child.tag == "alter":
                    alter = int(pitch_child.text)
                elif pitch_child.tag == "octave":
                    octave = pitch_child.text

            note_value = f"{note}{alter_dict[alter]}{octave}"
        elif child.tag == "duration":
            duration = int(child.text)
        elif child.tag == "voice":
            voice = int(child.text)
            if voice not in voice_progress:
                voice_progress[voice] = voice_progress[0]
        elif child.tag == "tie":
            tie_type_str = child.attrib["type"]
            if tie_type_str == "stop":
                tie_type = Note.TieType.STOP
            elif tie_type_str == "start":
                # middle ties represented by stop <tie> followed by start <tie>
                if tie_type == Note.TieType.STOP:
                    tie_type = Note.TieType.MIDDLE
                else:
                    tie_type = Note.TieType.START
        elif child.tag == "rest":
            rest = True

    
    # if this is the second note in a chord, need to change voice progress
    # to reflect this, since it will have been advanced when it should not have been
    if (chorded_with and 
        current_measure.get_last_added_note() != None and
        current_measure.get_last_added_note().chorded_with == None):

        voice_progress[voice] -= current_measure.get_last_added_note().duration
        voice_progress[0] -= current_measure.get_last_added_note().duration


    
    onset = voice_progress[voice]
    if (grace):
        onset -= GRACE_LENGTH

    # only advance progress if not a grace note
    if not(grace or chorded_with):
        # if just finished chord, advance chord
        if (chorded_with == None and 
            current_measure.get_last_added_note() != None and
            current_measure.get_last_added_note().chorded_with != None):

            chord_start = current_measure.get_last_added_note().get_chord_start()
            # assuming all notes in chord are in same voice

            if chord_start.voice == 0:
                voice_progress = {
                    voice: voice_progress[voice] + chord_start.duration for voice in voice_progress}
            else:
                voice_progress[chord_start.voice] += chord_start.duration
                voice_progress[0] += chord_start.duration

        if voice == 0:
            voice_progress = {
                voice: voice_progress[voice] + duration for voice in voice_progress}
        else:
            voice_progress[voice] += duration
            voice_progress[0] += duration

    if rest:
        return None

    note = Note(note_value, duration, onset, voice,
                tie_type=tie_type, chorded_with=chorded_with)

    return note


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


