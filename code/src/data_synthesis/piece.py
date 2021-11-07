class Piece:

    def __init__(self):
        """
        Constructor for Piece
        """
        self.measures = []

    def sort(self):
        """
        Sorts the current notes by onset time
        """
        for measure in self.measures:
            measure.sort()

        self.measures.sort(key=lambda measure: measure.onset)

    def from_parts(parts):
        """
        Creates a Piece object from a list of parts

        parts: list of Part objects
        """
        piece = Piece()
        if len(parts) == 0:
            return piece

        # now need to combine all the measures from each part
        # assuming measure in each part line up
        for i, measure in enumerate(parts[0].measures):
            all_measures = [part.measures[i] for part in parts]
            new_measure = Measure(measure.length, measure.divisions, measure.tempo, measure.onset)
            for measure in all_measures:
                for note in measure.notes:
                    new_measure.add_note(note)
            piece.measures.append(new_measure)

        return piece

    def __repr__(self):
        return self.measures.__repr__()

class Part:

    def __init__(self):
        """
        Constructor for Part
        """
        self.measures = []

    def add_measure(self, measure):
        """
        Adds a measure

        measure: Measure object to add
        """
        self.measures.append(measure)

    def get_last_measure(self):
        """
        Returns last measure in part
        """
        return self.measures[-1]

    def get_last_added_note(self):
        return self.get_last_measure().get_last_added_note()


class Measure:

    def __init__(self, length, divisions, tempo, onset):
        """
        Constructor for measure

        length: length of the measure in crotchets
        divisions: how many divisions crotchets are split into
        tempo: tempo of this measure in crotchets / minute
        onset: onset of this measure in the piece in crotchets
        """

        self.tempo = tempo
        self.notes = []
        self.divisions = divisions
        self.length = length
        self.onset = onset
        self.last_added_note = None

    def add_note(self, note):
        """
        Adds a Note object to the measure

        note: Note object to add
        """

        self.notes.append(note)
        self.last_added_note = note

    def get_last_added_note(self):
        """
        Returns the last added note (this is useful for ties)
        """
        return self.last_added_note

    def sort(self):
        """
        Sorts notes in the measure by time
        """

        self.notes.sort(key=lambda note: note.onset)

    def __repr__(self):
        return self.notes.__repr__()

