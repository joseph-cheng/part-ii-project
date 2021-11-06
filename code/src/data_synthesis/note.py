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

    def __init__(self, note_value, duration, tie=False, tied_from=None):
        """
        Constructor for Note

        note_value : integer representing MIDI note value (0-127) or human-readable note (e.g. D#4)
        duration: multiple of crotchets that represents the duration
        onset: number of crotchets since start of piece where note should start
        tied_from: a previous note that this note was tied from
        """

        if isinstance(note_value, str):
            # Need to find where octave starts, octave can be from -1 to 9
            split_loc = None
            for i, c in enumerate(note_value):
                if c[i:].isnumeric():
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
            if len(note > 1):
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
        self.tied = tied
