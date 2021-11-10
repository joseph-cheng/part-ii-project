import enum

class Note:

    NOTE_VALUES = {
        "C": 0,
        "D": 2,
        "E": 4,
        "F": 5,
        "G": 7,
        "A": 9,
        "B": 11,
    }

    # used for __repr__
    REVERSE_NOTE_VALUES = {
            0:  "C",
            1:  "C#",
            2:  "D",
            3:  "D#",
            4:  "E",
            5:  "F",
            6:  "F#",
            7:  "G",
            8:  "G#",
            9:  "A",
            10: "A#",
            11: "B",
    }

    class TieType(enum.Enum):
        NONE = enum.auto()
        STOP = enum.auto()
        START = enum.auto()
        MIDDLE = enum.auto()


    def __init__(self, note_value, duration, onset, voice, velocity=127, tied_from=None, tie_type=TieType.NONE, chorded_with=None):
        """
        Constructor for Note

        note_value : integer representing MIDI note value (0-127) or human-readable note (e.g. D#4)
        duration: number of divisions in the particular measure that represents duration
        onset: number of divisions in particular measure since start of measure where note should start
        voice: what mxml voice this note is in
        velocity: number from 0-127 that is the MIDI velocity of this note
        tied_from: a previous note that this note was tied from
        tie_type: the type of tie, if this note is tied
        chorded_with: the previous note that this note is in a chord with
        """

        if isinstance(note_value, str):
            # Need to find where octave starts, octave can be from -1 to 9
            split_loc = None
            for i, c in enumerate(note_value):
                if note_value[i:].isnumeric():
                    split_loc = i
                    break

            octave = None
            note = None
            if split_loc == None:
                print(
                    f"ERROR: Failed to find octave for note: {note_value}, defaulting to 4.\nSetting note to {note_value}"
                )
                octave = 4
                note = note_value
            else:
                octave = int(note_value[split_loc:])
                note = note_value[:split_loc]

            # calculate MIDI number

            accidental_factor = 0
            # if len(note) > 1, then it will be followed by #, x, b, or bb
            if len(note):
                if note[1:] == '#':
                    accidental_factor = 1
                elif note[1:] == 'x':
                    accidental_factor = 2
                elif note[1:] == 'b':
                    accidental_factor = -1
                elif note[1:] == 'bb':
                    accidental_factor = -2

            note_number = (
                (octave + 1) * 12 +
                Note.NOTE_VALUES[note[0]] + accidental_factor
            )

            self.note_value = note_number
        else:
            if not (0 <= note_value <= 127):
                print(
                    f"ERROR: Note value {note_value} out of bounds. Limiting to 0-127"
                )
                note_value = min(127, max(0, note_value))
            self.note_value = note_value

        self.duration = duration
        self.onset = onset
        self.tied_from = tied_from
        self.tie_type = tie_type
        self.chorded_with = chorded_with
        self.velocity = velocity
        self.voice = voice

    def get_tie_start(self):
        """
        Gets the first note in a tie by traversing the linked list of tied notes

        returns: Note object that is the first in a tie
        """
        if self.tie_type == TieType.START:
            return self
        elif self.tie_type == TieType.MIDDLE or self.tie_type == TieType.STOP:
            return self.tied_from.get_tie_start()

    def get_chord_start(self):
        """
        Gets the first note in a chord by traversing the linked list of chorded notes

        returns: Note object that was the first in the chord
        """
        if self.chorded_with == None:
            return self
        return self.chorded_with.get_chord_start()

    def __repr__(self):
        octave = (self.note_value // 12)
        note = Note.REVERSE_NOTE_VALUES[self.note_value - octave * 12]

        return f"({note}{octave-1}, onset: {self.onset}, duration: {self.duration})"
    
    def duration_in_seconds(self, tempo, divisions):
        """
        Gets the duration of the note in seconds

        tempo: tempo in the measure where this note is played
        divisions: divisions in the measure where this note is played

        returns: duration of the note in seconds
        """
        return self.duration/divisions * (1/tempo) * 60

    def convert_to_seconds(self, measure):
        """
        Assuming the parent measure has been converted to seconds, converts this note's timing to seconds

        measure: parent Measure object

        returns: nothing
        """

        self.duration = self.duration/measure.divisions * (1/measure.tempo) * 60
        self.onset = measure.onset + self.onset/measure.divisions * (1/measure.tempo) * 60

    def get_midi_note(self):
        """
        Gets the midi note value of this note

        returns: the midi note value corresponding to this note's pitch
        """
        return self.note_value
