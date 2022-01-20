from dataclasses import dataclass

from english_words import english_words_lower_set
from typing import NamedTuple, List, Dict
import re

BLACK = 'black'

GREEN = 'green'

YELLOW = 'yellow'


@dataclass
class Mask:
    letter: str
    index: int
    color: str


@dataclass
class Guess:
    word: str
    result: List[Mask]


@dataclass
class GameResult:
    is_win: bool
    num_tries: int


class Strategy:
    def make_guess(self, previous_guesses: List[Guess]) -> str:
        pass


class CommonLettersStrategy(Strategy):
    letter_counts: Dict[str, int]
    words: List[str]

    def __init__(self):
        self.words = get_words()
        self.letter_counts = get_common_letters(self.words)
        sort_words_by_common_letters(self.words, self.letter_counts)

    def make_guess(self, previous_guesses: List[Guess]):
        return next(filter_words_by_mask(self.words, [previous_guess_result
                                                      for previous_guess in previous_guesses
                                                      for previous_guess_result in
                                                      previous_guess.result]))


def get_words():
    return list(filter(lambda word: len(word) == 5, english_words_lower_set))


def get_common_letters(words):
    letter_counts = {}
    for word in words:
        seen_letters = {}
        for letter in word:
            if letter not in seen_letters:
                if letter.lower() not in letter_counts:
                    letter_counts[letter.lower()] = 0
                letter_counts[letter.lower()] += 1
                seen_letters[letter] = True
    print(letter_counts)
    return letter_counts


def sort_words_by_common_letters(words=[], letter_counts={}):
    # common_letters = list(letter_counts.keys())
    # common_letters.sort(reverse=True, key=lambda x: letter_counts[x])
    # print(common_letters)
    #
    # Score each word by summing the letter_counts for each letter in the word
    score_by_word = {}
    for word in words:
        if word not in score_by_word:
            score_by_word[word] = 0
        seen_letters = {}
        for letter in word:
            if letter not in seen_letters:
                score_by_word[word] += letter_counts[letter]
                seen_letters[letter] = True

    words.sort(reverse=True, key=lambda x: score_by_word[x])
    print(words)


def filter_words_by_mask(words: List[str], mask_items: List[Mask]):
    running_filter = filter(lambda x: True, words)

    def get_masker_for_mask_item(mask_item: Mask):
        def _match_mask_against_word(word):
            # TODO: lotta 'in word' checks; are those efficient?  hashify/setify the word?
            if mask_item.color == GREEN:
                if word[mask_item.index] == mask_item.letter:
                    return True
            if mask_item.color == YELLOW:
                if mask_item.letter in word \
                        and word.index(mask_item.letter) != mask_item.index:
                    return True
            if mask_item.color == BLACK:
                if mask_item.letter not in word:
                    return True
            return False

        return _match_mask_against_word

    for mask_item in mask_items:
        running_filter = filter(get_masker_for_mask_item(mask_item), running_filter)
    return running_filter


def parse_mask(guess='', mask=''):
    mask_items: List[Mask] = []
    color_map = {
        'b': BLACK,
        'y': YELLOW,
        'g': GREEN
    }
    for i in range(5):
        mask_items.append(Mask(letter=guess[i], index=i, color=color_map[mask[i]]))
    return mask_items


def evaluate_guess(guess: str, answer: str):
    mask_items: List[Mask] = []
    for i in range(5):
        if answer[i] == guess[i]:
            mask_items.append(Mask(letter=guess[i], index=i, color=GREEN))
        elif guess[i] in answer:
            mask_items.append(Mask(letter=guess[i], index=i, color=YELLOW))
        else:
            mask_items.append(Mask(letter=guess[i], index=i, color=BLACK))
    return mask_items


def simulate_game(answer: str, strategy: Strategy):
    num_turns = 0
    latest_guess = ''
    previous_guesses: List[Guess] = []
    while num_turns < 5 and latest_guess != answer:
        latest_guess = strategy.make_guess(previous_guesses)
        print(latest_guess)
        mask_items = evaluate_guess(latest_guess, answer)
        previous_guesses.append(Guess(latest_guess, mask_items))
        num_turns += 1
    return GameResult(is_win=num_turns <= 5 and latest_guess == answer, num_tries=num_turns)


# TODO: SQL table with 5 columns, one for each position of word

print(simulate_game('proxy', CommonLettersStrategy()))
