class Piece:

    def __init__(self, tempo):
        """
        Constructor for Piece

        tempo: number of crotchets per minute
        """
        self.measures = []
        self.tempo = tempo

    def sort(self):
        """
        Sorts the current notes by onset time
        """
        for measure in self.measures:
            measure.sort()

    def from_parts(parts):
        """
        Creates a Piece object from a list of parts

        parts: list of Part objects
        """
        piece = Piece(tempo)
        piece.measures = [measure for part in parts for measure in part.measures]
        return piece

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


class Measure:

    def __init__(self, length, divisions, tempo=120):
        """
        Constructor for measure

        length: length of the measure in crotchets
        divisions: how many divisions crotchets are split into
        tempo: tempo of this measure in crotchets / minute
        """

        self.tempo = tempo
        self.notes = []
        self.divisions = divisions
        self.length = length

    def add_note(self, note):
        """
        Adds a Note object to the measure

        note: Note object to add
        """
        self.notes.append(note)

    def sort(self):
        """
        Sorts notes in the measure by time
        """

        self.notes.sort(key=lambda note: note.onset)

