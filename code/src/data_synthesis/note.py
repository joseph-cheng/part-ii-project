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


    def __init__(self, note_value, duration, onset, tied_from=None, tie_type=TieType.NONE, chorded_with=None):
        """
        Constructor for Note

        note_value : integer representing MIDI note value (0-127) or human-readable note (e.g. D#4)
        duration: number of divisions in the particular measure that represents duration
        onset: number of divisions in particular measure since start of measure where note should start
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

    def get_tie_start(self):
        if self.tie_type == TieType.START:
            return self
        elif self.tie_type == TieType.MIDDLE or self.tie_type == TieType.STOP:
            return self.tied_from.get_tie_start()

    def get_chord_start(self):
        if self.chorded_with == None:
            return self
        return self.chorded_with.get_chord_start()

    def __repr__(self):
        octave = (self.note_value // 12)
        note = Note.REVERSE_NOTE_VALUES[self.note_value - octave * 12]

        return f"({note}{octave-1}, {self.duration})"



