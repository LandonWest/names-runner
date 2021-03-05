import argparse
import csv
import json
import os
import subprocess
import sys

from colorama import (
    Back,
    Fore,
    Style,
    init as colorama_init,
)


class NamesRunner():

    ACTIONS = ('Like', 'Dislike', 'Undecided')
    POSITIVE_CHOICES = ('yes', 'ya', 'yep', 'y')
    NEGATIVE_CHOICES = ('no', 'nope', 'n')
    NEUTRAL_CHOICES = ('undecided', 'u', 'maybe')
    VALID_CHOICES = POSITIVE_CHOICES + NEGATIVE_CHOICES + NEUTRAL_CHOICES
    QUIT_OPTIONS = ('q', 'quit', 'exit')

    def __init__(self, gender: str, start_name: str = None):
        self.start_name = start_name.upper() if start_name else None
        self.gender = gender
        self.in_file = self.get_in_file()
        self.out_file = self.get_out_file()

        colorama_init(autoreset=True)

    def get_in_file(self):
        if self.gender == 'boy':
            return os.getcwd() + '/source_names/ENGivenMale.json'

        if self.gender == 'girl':
            return os.getcwd() + '/source_names/ENGivenFemale.json'

    def get_out_file(self):
        out_file = f"{self.gender}_name_votes.csv"
        path_exists = os.path.exists(os.getcwd() + "/" + out_file)
        if path_exists and not self.start_name:
            print(
                Fore.RED
                + f"'{out_file}' already exists. Either pass a start_name or remove the file to start over"
            )
            sys.exit()

        return out_file

    def save_response(self, csv_writer, name, answer):
        answer_key = {
            'Y': [name, 'X', '', ''],
            'N': [name, '', 'X', ''],
            'U': [name, '', '', 'X'],
        }

        csv_writer.writerow(answer_key[answer])

    def check_quit(
        self, answer: str, quit_on_name: str, gender_abbreviation: str
    ) -> None:

        answer = answer.lower()
        gender = 'girl' if gender_abbreviation == 'F' else 'boy'

        if answer in NamesRunner.QUIT_OPTIONS:
            print("Ok, we'll stop here!")

            rerun_output = 'python {} --gender {} --start_name {}'.format(
                os.path.basename(__file__),
                gender,
                quit_on_name
            )
            print(
                Style.DIM
                + f'Your responses have been written to "{self.out_file}".\n'
                + f'To start again where you left off run `{rerun_output}`\n'
                + "I've copied that to the clipboard to make it easier on you ;)"
            )
            self.write_to_clipboard(rerun_output)

            return sys.exit()


    def get_prompt_answer(self, name: str, gender_abbreviation: str) -> tuple:
        color = Fore.MAGENTA if gender_abbreviation == 'F' else Fore.BLUE

        retry = True
        while retry:
            print(f'Do you like the name {color}{name}?')
            answer = input().lower()

            self.check_quit(answer, name, gender_abbreviation)
            if answer not in (NamesRunner.VALID_CHOICES):
                print(
                    'Unrecognized response. Type "y", "n", or "u" for undecided.'
                )
                continue

            retry = False

        if answer in NamesRunner.POSITIVE_CHOICES:
            answer = "Y"
        if answer in NamesRunner.NEGATIVE_CHOICES:
            answer = "N"
        if answer in NamesRunner.NEUTRAL_CHOICES:
            answer = "U"

        return name, answer

    def write_to_clipboard(self, output):
        process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE)
        process.communicate(output.encode('utf-8'))

    def run(self):
        spacer = ' ' * 21
        dashes = '-' * 57

        print(dashes)
        print(
            Back.CYAN
            + spacer
            + Style.BRIGHT
            + Fore.WHITE
            + 'Name That Baby!'
            + spacer
        )
        print(dashes)
        print(
            Style.DIM
            + 'Actions: yes (y), no (n), undecided (u), quit (q)'
        )
        print()

        with open(self.in_file) as json_file:
            data = json.load(json_file)

            out_file = f"{self.gender}_name_votes.csv"

            with open(out_file, 'a', newline='') as outfile:
                csv_writer = csv.writer(outfile)
                if not self.start_name:
                    csv_writer.writerow(['Name', 'Like', 'Dislike', 'Undecided'])

                keep_going = False
                for name_obj in data:
                    if name_obj['name'] == self.start_name:
                        keep_going = True

                    if (
                            not self.start_name
                            or (self.start_name and name_obj['name'] == self.start_name)
                            or keep_going
                        ):
                            name, answer = self.get_prompt_answer(
                                name_obj['name'],
                                name_obj.get('gender', 'M'),
                            )
                            self.save_response(csv_writer, name, answer)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Baby Names')
    parser.add_argument(
        '-s',
        '--start_name',
        help='The name you want to pick back up with or the last name in your vote list'
    )
    parser.add_argument(
        '-g',
        '--gender',
        required=True,
        choices=('boy', 'girl'),
        help='The gender of names you want to look at - boy or girl'
    )
    args = parser.parse_args()

    names_program = NamesRunner(args.gender, args.start_name)
    names_program.run()
