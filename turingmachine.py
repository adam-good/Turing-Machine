from time import sleep
from string import ascii_lowercase
import argparse

class Tape():
    """A wrapper around a python list to act as a Tape for a Turing Machine
    """

    class direction:
        """Enumeration type for the directions on the tape (left,right,stay)
        """
        right = 'R'
        left = 'L'
        stay = 'S'

    class char_codes:
        """enumeration type for character codes used in printing
        """
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    def __init__(self, initial_state='hello', start_size=None):
        """A wrapper around a python list to act as a Tape for a Turing Machine

        Keyword Arguments:
            initial_state {str} -- The initial text on the tape (default: {'hello'})
            start_size {int} -- The initial size of the tape if initial_state is None. Ignored if initial_state is not None (default: {None})
        """
        self._loc = 0

        if initial_state:
            self._list = list(initial_state)
            # self._expand_left(3)
            # self._expand_right(3)
        else:
            if start_size:
                self._list = [None] * start_size
            else:
                self._list = []

        self._min_loc = 0
        self._max_loc = self._get_max_loc()

    def _expand_left(self, n_spaces):
        self._loc = self._loc + n_spaces
        new_left = [None] * n_spaces
        self._list = new_left + self._list
        self._max_loc = self._get_max_loc()
    
    def _expand_right(self, n_spaces):
        new_right = [None] * n_spaces
        self._list = self._list + new_right
        self._max_loc = self._get_max_loc()

    def _get_max_loc(self):
        return len(self._list) - 1

    def move_left(self):
        """Move the head on the tape one spot to the left
        """
        if self._loc == self._min_loc:
            self._expand_left(1)
        self._loc -= 1

    def move_right(self):
        """Move the head on the tape one spot to the right
        """
        if self._loc == self._max_loc:
            self._expand_right(1)
        self._loc += 1

    def get_char(self):
        """Return the value on the tape at its current location

        Returns:
            chr -- the value on the tape at its current location
        """
        return self._list[self._loc]

    def set_char(self, value):
        """Sets the value of the current place on the tape to value

        Arguments:
            value {str} -- value to be set onto the tape
        """
        self._list[self._loc] = value

    def get_string(self):
        """Get the current state of the tape as a string

        Returns:
            str -- current state of the tape as a string
        """
        return ''.join([item for item in self._list if item != None])

    def draw(self):
        """Draw the current state of the tape in the terminal
        """
        list_enum = enumerate(self._list)
        
        def draw_tape():
            for i,item in list_enum:
                out = f'{self.char_codes.UNDERLINE}{item}{self.char_codes.END}' if item != None else f'{self.char_codes.UNDERLINE} {self.char_codes.END}'
                if i == self._loc:
                    print(f'{self.char_codes.RED}{out}{self.char_codes.END}', end='')
                else:
                    print(f'{out}', end='')
            print(' ', end='\r')

        draw_tape()
        # draw_head()


class TuringMachine():
    """Implimentation of a Turing Machine
    """
    def __init__(self, initial_tape, initial_state, states, accepting_states, rejecting_states, transitions):
        """Implementation of a Turing Machine

        Arguments:
            initial_tape {Tape} -- The tape to be used by the machine
            initial_state {int} -- The numeric value of the starting state of the machine
            states {list[int]} -- List of integers the represent the states of the machine
            accepting_states {list[int]} -- List of integers that represent the accepting states of the machine
            rejecting_states {list[int]} -- List of integers that represent the rejecting states of the machine
            transitions {dict[tuple]} -- Dictionary that acts as the transition function (takes in (state,input) and returns (next_state, output, direction))
        """
        self.tape = initial_tape #Tape(initial_state=initial_input)
        self.states = states
        self.current_state = initial_state
        self.current_input = self.tape.get_char()
        
        self._accepting_states = accepting_states
        self._rejecting_states = rejecting_states
        self._transition_fn = transitions

    def run(self, draw=False, print_configs=False):
        """Iterate the turing machine until it enters an accepting or rejecting state

        Keyword Arguments:
            draw {bool} -- If True, draw the tape on each iteration (default: {False})
            print_configs {bool} -- If True, print the configuration on each iteration. Overrides draw. (default: {False})

        Returns:
            str -- The final state of the tape as a string
        """
        while self.current_state not in self._accepting_states:
            self.advance()

            if print_configs:
                draw = False
                next_state, output, direction = self._transition_fn[(self.current_state, self.current_input)]
                print(f'({self.current_state}, {self.current_input}, {output}, {next_state}, {direction})')
                sleep(0.2)

            if draw == True:
                self.tape.draw()
                sleep(0.2)
        return self.tape.get_string()

    def advance(self):
        """Advance the configuration of the turing machine by changing states, reading/writing, and moving the tape
        """
        self.current_input = self.tape.get_char()
        current_config = (self.current_state, self.current_input)
        next_config = self._transition_fn[current_config]
        next_state, char_out, direction = next_config

        self.current_state = next_state
        self.tape.set_char(char_out)
        if direction == Tape.direction.right:
            self.tape.move_right()
        elif direction == Tape.direction.left:
            self.tape.move_left()
        elif direction == Tape.direction.stay:
            pass
        

if __name__ == "__main__":
    # This is just making it easier for me to set up the transition functions
    # This doesn't actually affect how the turing machine works, just saves me time in writing a whole bunch of state transitions
    def cipher(c, shift=5):
        byte = ord(c) - ord('a')
        byte = (byte + shift) % len(ascii_lowercase)
        return chr(byte + ord('a'))


    parser = argparse.ArgumentParser()
    parser.add_argument('plaintext', type=str, help="The input to be encrypted")
    parser.add_argument('shift', type=int, help='The shift value for encryption')

    args = parser.parse_args()
    string = args.plaintext
    shift = args.shift

    tape = Tape(initial_state=string)
    states = [0,1,2]
    accepting_states = [2]
    transitions = {}
    for c in ascii_lowercase:
        transitions[(0,c)] = (1,c, Tape.direction.stay)
        transitions[(1,c)] = (1, cipher(c, shift=shift), Tape.direction.right)
        transitions[(1,None)] = (2,None, Tape.direction.stay)
    
    for s in states:
        transitions[(s,' ')] = (s, ' ', Tape.direction.right)

    T_encrypt = TuringMachine(tape, 0, states, [2], [], transitions)
    ciphertext = T_encrypt.run(draw=True, print_configs=False)

    print()

    tape = Tape(initial_state=ciphertext)

    states = [0,1,2]
    accepting_states = [2]
    transitions = {}
    for c in ascii_lowercase:
        transitions[(0,c)] = (1,c, Tape.direction.stay)
        transitions[(1,c)] = (1, cipher(c, shift=-shift), Tape.direction.right)
        transitions[(1,None)] = (2,None, Tape.direction.stay)
    
    for s in states:
        transitions[(s,' ')] = (s, ' ', Tape.direction.right)
    T_decrypt = TuringMachine(tape, 0, states, [2], [], transitions)
    plaintext = T_decrypt.run(draw=True)

    print()