from piece import Piece
from profile import Profile
from mxl_parser import parse_mxml
from note import Note
import numpy as np
import fluidsynth
import scipy.io.wavfile

def generate_audio(mxml_filename, soundfont_filename, wavfile_output, profile):
    """
    Generates audio from a mxml filename and writes the output to a wavfile

    mxml_filename: path to a mxml file
    soundfont_filename: path to a soundfont to use for fluidsynth
    wavfile_output: filename to write the resulting wavfile to
    profile: Profile object corresponding to a particular pianist profile

    returns: nothing
    """
    EPSILON = 1e-5

    SAMPLE_RATE = 44100

    piece = parse_mxml(mxml_filename)
    piece = piece.convert_to_seconds()
    piece = piece.apply_profile(profile)

    piece.sort()

    samples = []
    piano = fluidsynth.Synth()
    piano_id = piano.sfload(soundfont_filename)
    piano.program_select(0, piano_id, 0, 0)

    # list of (Note, time_left) pairs of notes currently playing and how long they have left until finished
    notes_playing = []

    # how many seconds we are through the piece
    current_position = 0

    note_generator = piece.get_notes()
    next_note = next(note_generator, None)

    while next_note != None or len(notes_playing) > 0:
        # check if there is a noteoff or noteon event next
        if next_note == None or ((next_note.onset - current_position) > min([pair[1] for pair in notes_playing], default=9e99)):
            # noteoff event next

            time_until_noteoff = min([pair[1] for pair in notes_playing])
            min_note = min(notes_playing, key=lambda pair:pair[1])[0]

            # so, generate samples until noteoff event begins
            # only generate samples if time passes
            if (time_until_noteoff > EPSILON):
                samples.append(piano.get_samples(int(SAMPLE_RATE * time_until_noteoff)))

            if min_note.tie_type == Note.TieType.NONE or min_note.tie_type == Note.TieType.STOP:
                piano.noteoff(0, min_note.get_midi_note())
            current_position += time_until_noteoff
            notes_playing.remove((min_note, time_until_noteoff))
            notes_playing = [(note, duration - time_until_noteoff) for note, duration in notes_playing]
        else:
            # noteon event next

            # so, generate samples until noteon event begins
            # only generate samples if time has actually passed (e.g. not a chord)
            if (next_note.onset - current_position > EPSILON):
                samples.append(piano.get_samples(int(SAMPLE_RATE * (next_note.onset - current_position))))

            # then, turn on the note
            if next_note.tie_type == Note.TieType.NONE or next_note.tie_type == Note.TieType.START:
                piano.noteon(0, next_note.get_midi_note(), next_note.velocity)
            # update notes playing time left
            notes_playing = [(note, duration - (next_note.onset - current_position)) for note, duration in notes_playing]
            # advance current position
            current_position = next_note.onset
            # add just played note to the list of notes playing
            notes_playing.append((next_note, next_note.duration))
            # and move on to the next note
            next_note = next(note_generator, None)

    piano.delete()

    samples = np.concatenate(samples)

    scipy.io.wavfile.write(wavfile_output, SAMPLE_RATE, samples)

profile = Profile()

profile.tempo_envelope = lambda t: (np.sin(10 * np.pi * t) / 5) + 1
profile.set_normal_onset_distribution(0, 0.02)
profile.set_binom_amplitude_distribution(100)

generate_audio("/home/joe/Documents/cambridge/ii/part-ii-project/code/res/scores/chopin__trois_valses.xml", "/home/joe/Documents/cambridge/ii/part-ii-project/code/res/soundfonts/yamaha_grand.sf2", "output.wav", profile)
