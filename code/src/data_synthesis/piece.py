import copy

class Piece:

    def __init__(self):
        """
        Constructor for Piece
        """
        self.measures = []
        self.sorted = False
        self.in_seconds = False

    def sort(self):
        if self.sorted:
            return
        """
        Sorts the current notes by onset time
        """
        for measure in self.measures:
            measure.sort()

        self.measures.sort(key=lambda measure: measure.onset)
        self.sorted = True

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


    def calculate_tempo(self):
        """
        Calculates `global' tempo, a little rudimentary currently

        returns: some measure of the global tempo of a piece
        """

        # currently unweighted average of tempo of each measure
        return sum(measure.tempo for measure in self.measures)/len(self.measures)



    def __repr__(self):
        return "\n".join(map(lambda x: x.__repr__(), self.measures))

    def get_notes(self):
        """
        generator for returning each note in a piece in order

        returns: a generator for each Note in order
        """
        self.sort()
        for measure in self.measures:
            for note in measure.notes:
                yield note

    def convert_to_seconds(self):
        """
        Converts timing in the piece's measures and notes into seconds

        returns: a new piece object with timings in seconds
        """

        new_piece = copy.deepcopy(self)

        new_piece.sort()

        last_measure = None

        for measure in new_piece.measures:
            measure.convert_to_seconds(last_measure)
            last_measure = measure

        new_piece.in_seconds = True
        return new_piece

    def apply_profile(self, profile):
        """
        Convert to seconds (if not already), and apply a pianist profile to slightly modify the performance of a piece

        profile: Profile object 

        returns: a new piece with modified attributes based on the pianist profile
        """

        piece = copy.deepcopy(self)

        piece.sort()

        piece_length = piece.measures[-1].onset + piece.measures[-1].length
        piece_tempo = piece.calculate_tempo()

        for measure in piece.measures:
            normalized_onset = measure.onset / piece_length
            # tempo envelope gives us a scaling factor, which we multiply by the `global' tempo of our piece
            measure.tempo = profile.tempo_envelope(normalized_onset) * piece_tempo

        # now we have applied tempo envelope, so we apply amplitude and onset offset distributions
        piece = piece.convert_to_seconds()

        for measure in piece.measures:
            for note in measure.notes:
                note.velocity = profile.amplitude_distribution()
                note.onset += profile.onset_distribution()

        piece.sorted = False
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

        if note != None:
            self.notes.append(note)
        self.last_added_note = note

    def get_last_added_note(self):
        """
        Returns the last added note (this is useful for ties)
        """
        return self.last_added_note

    def convert_to_seconds(self, previous_measure):
        """
        Assuming the previous measure has been converted to seconds (if this is not the initial measure), convert this measure's timing to seconds

        previous_measure: previous Measure object
        """

        if previous_measure == None:
            self.onset = 0
        else:
            self.onset = previous_measure.onset + previous_measure.length

        self.length = self.length * (1/self.tempo) * 60

        for note in self.notes:
            note.convert_to_seconds(self)




    def sort(self):
        """
        Sorts notes in the measure by time
        """

        self.notes.sort(key=lambda note: (note.onset, note.duration))

    def __repr__(self):
        return f"Measure onset: {self.onset}\nMeasure length: {self.length}\n{self.notes.__repr__()}\n"

