from spec.puzzle.examples.reddot.y2020 import the_illuminator_util

ADJACENCY_BIT_MAP = [
    0b00000000000000000000000000000000000000000000011111,
    0b00000000000000000000000000000000000000001010000011,
    0b00000000000000000000000000000000000010000000000101,
    0b00000000000000000000000000000010000000000000001001,
    0b00000000000000000000000000001000000100000000010001,
    0b00000000000000001000000000000000000000011001100000,
    0b00000000000000000000000000000000000001000001100000,
    0b00000000000001010000000000000000000000100010000010,
    0b00000000000000000000000000000000100000000100000000,
    0b00000000000000000000000000000000001000001000100010,
    0b00000000000000000000000000000000000000010000100000,
    0b00000000000000000000000000000000000001100010000000,
    0b00000000000000000000000000000000000001100001000000,
    0b00000000000000000000000100000001000010000000000100,
    0b00000000000000000010000000000000001100000000010000,
    0b00000000000000000100000000010000001100001000000000,
    0b00000000000000000000000000100000010000000000000000,
    0b00000000000000000000000000000001100000000100000000,
    0b00000000000000000000000000000001100010000000000000,
    0b00000000000000000000001000000110000000000000001000,
    0b00100010000000000000000000000110000000000000000000,
    0b00000000000000000000000010001000000000000000010000,
    0b00000000000000001100000000110000001000000000000000,
    0b00000000000000000000000000110000010000000000000000,
    0b00000000000000000001000011000000000000000000000000,
    0b00000000000000000001000011001000000000000000000000,
    0b00000000000000000000101100000000000010000000000000,
    0b00000000100100100000001100000010000000000000000000,
    0b00000000001000000011010000000000000000000000000000,
    0b00000000000000100000100100000000000000000000000000,
    0b00000000000000000001010011000000000000000000000000,
    0b00000000000001000010010000000000000100000000000000,
    0b00000000000001001100000000010000001000000000000000,
    0b00000000000000001100000000010000000000000000100000,
    0b00000000000000010000000000000000000000000010000000,
    0b00000000000010100000101000000000000000000000000000,
    0b00000000000101000110000000000000000000000010000000,
    0b00000000000010100000000000000000000000000000000000,
    0b00000001001101000000001000000000000000000000000000,
    0b00000001011100000000010000000000000000000000000000,
    0b00000001011000000000000000000000000000000000000000,
    0b00001000100000000000001000000000000000000000000000,
    0b10001001011100000000000000000000000000000000000000,
    0b01000110000000000000000000000100000000000000000000,
    0b00000110000000000000000000000000000000000000000000,
    0b01111001100000000000000000000000000000000000000000,
    0b10011000000000000000000000000000000000000000000000,
    0b00101000000000000000000000000100000000000000000000,
    0b01001010000000000000000000000000000000000000000000,
    0b10010001000000000000000000000000000000000000000000,
]

TARGET_VALUE = 2 ** len(ADJACENCY_BIT_MAP) - 1

ADJACENCY_LIST = the_illuminator_util.bit_map_to_adjacency_list(
    ADJACENCY_BIT_MAP)
