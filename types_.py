from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Literal

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from _typeshed import SupportsDunderLT

from strenum import PascalCaseStrEnum
from enum import auto, StrEnum, IntEnum, Enum
from sqlite3 import Cursor
from typing import override


class Id(int):
    __MIN, __MAX = 1, 722
    MEGAMORPH = 657

    def validate(self) -> None:
        if not Id.__MIN <= self <= Id.__MAX:
            raise ValueError(
                f"IDs must be between '{Id.__MIN}' and '{Id.__MAX}'. "
                f"Received {repr(self)}."
            )


class Stat(int):
    @override
    def __neg__(self) -> Stat:
        return Stat(-super())


class EquipStage(int):
    # This seems to allow classic integer operations to conserve the custom type,
    # ... contrary to `NewType(..., int)`.
    pass


class Position:  # (SupportsDunderLT):

    class Mode(IntEnum):
        # Mode = offset
        HAND = 0
        DECK = 0
        FRONTROW = 5
        BACKROW = 10

    __MIN_BOARD_IDX = 0
    __MAX_BOARD_IDX = 4  # inclusive

    def __init__(self, idx: int, mode: Position.Mode):
        self.mode: Position.Mode = mode
        self.idx: int = idx
        self.__update_pos()

    def __le__(self, other) -> bool:
        if type(other) is int:
            return self.pos <= other

        if not isinstance(other, Position):
            return False

        return self.pos <= other.pos

    def __lt__(self, other) -> bool:
        if type(other) is int:
            return self.pos < other

        if not isinstance(other, Position):
            return False

        return self.pos < other.pos

    @override
    def __eq__(self, other) -> bool:
        if id(self) == id(other):
            return True

        if type(other) is int:
            return self.pos == other

        if not isinstance(other, Position):
            return False

        return self.pos == other.pos

    def __ge__(self, other) -> bool:  # TODO: is there a way to infer that automatically from __le/eq__ ?
        if type(other) is int:
            return self.pos >= other

        if not isinstance(other, Position):
            return False

        return self.pos >= other.pos

    def __repr__(self) -> str:
        return repr(self.pos)

    @property
    def idx(self) -> int:
        return self._idx

    @idx.setter
    def idx(self, idx: int) -> None:
        if self.mode != Position.Mode.HAND and not (Position.__MIN_BOARD_IDX <= idx <= Position.__MAX_BOARD_IDX):
            raise ValueError(
                f'Invalid index {idx}. '
                f'Expecting value between {Position.__MIN_BOARD_IDX} and {Position.__MAX_BOARD_IDX} inclusive.'
            )
        self._idx = idx

    @property
    def mode(self) -> Position.Mode:
        return self._mode

    @mode.setter
    def mode(self, mode: Position.Mode) -> None:
        self._mode = mode

    @property
    def pos(self) -> int:
        return self._pos

    def __update_pos(self) -> None:
        self._pos = self.idx - self.mode.value


class StringSearchableEnum(PascalCaseStrEnum):
    @classmethod
    def by_name(cls, name: str | None, raise_if_not_found: bool = False) -> StringSearchableEnum | None:
        if name is None:
            return None

        for enum in cls:
            if enum.value == name.capitalize():
                return enum

        if raise_if_not_found:
            raise ValueError(f'Unknown enum name {repr(name)}.')

        return None

    @override
    def __repr__(self):
        return self.value


class Field(StringSearchableEnum):
    """ Order compatible with AI routines. """
    FOREST = auto()
    WASTELAND = auto()
    MOUNTAIN = auto()
    SOGEN = auto()
    UMI = auto()
    YAMI = auto()
    NONE = auto()  # Beware that `None` (NoteType) is NOT a Field, but NONE (str 'None') is


class Type(StringSearchableEnum):
    AQUA = auto()
    BEAST = auto()
    BEAST_WARRIOR = 'Beast-Warrior'
    DINOSAUR = auto()
    DRAGON = auto()
    FAIRY = auto()
    FIEND = auto()
    FISH = auto()
    INSECT = auto()
    MACHINE = auto()
    PLANT = auto()
    PYRO = auto()
    REPTILE = auto()
    ROCK = auto()
    SEA_SERPENT = 'Sea Serpent'
    SPELLCASTER = auto()
    THUNDER = auto()
    WARRIOR = auto()
    WINGED_BEAST = 'Winged Beast'
    ZOMBIE = auto()

    EQUIP = auto()
    MAGIC = auto()
    RITUAL = auto()
    TRAP = auto()


_monsters: set[Type] = {
    Type.AQUA,
    Type.BEAST,
    Type.BEAST_WARRIOR,
    Type.DINOSAUR,
    Type.DRAGON,
    Type.FAIRY,
    Type.FIEND,
    Type.FISH,
    Type.INSECT,
    Type.MACHINE,
    Type.PLANT,
    Type.PYRO,
    Type.REPTILE,
    Type.ROCK,
    Type.SEA_SERPENT,
    Type.SPELLCASTER,
    Type.THUNDER,
    Type.WARRIOR,
    Type.WINGED_BEAST,
    Type.ZOMBIE
}


def is_monster(type_: Type) -> bool:
    return type_ in _monsters


_non_monsters: set[Type] = {
    Type.EQUIP,
    Type.MAGIC,
    Type.RITUAL,
    Type.TRAP
}


def is_non_monster(type_: Type) -> bool:
    return type_ in _non_monsters


_field_types_boosted: dict[Field, set[Type]] = {
    Field.FOREST: {Type.BEAST, Type.BEAST_WARRIOR, Type.INSECT, Type.PLANT},
    Field.MOUNTAIN: {Type.DRAGON, Type.THUNDER, Type.WINGED_BEAST},
    Field.SOGEN: {Type.BEAST_WARRIOR, Type.WARRIOR},
    Field.UMI: {Type.AQUA, Type.SEA_SERPENT, Type.THUNDER},
    Field.WASTELAND: {Type.DINOSAUR, Type.ROCK, Type.ZOMBIE},
    Field.YAMI: {Type.FIEND, Type.SPELLCASTER}
}


def is_boosted_by(type_: Type, field: Field) -> bool:
    return type_ is not None and field in _field_types_boosted and type_ in _field_types_boosted[field]


_field_types_nerfed: dict[Field, set[Type]] = {
    Field.UMI: {Type.MACHINE, Type.PYRO},
    Field.YAMI: {Type.FAIRY}
}


def is_nerfed_by(type_: Type, field: Field) -> bool:
    return type_ is not None and field in _field_types_nerfed and type_ in _field_types_nerfed[field]


class BattleMode(StringSearchableEnum):
    DEFENSE = auto()
    ATTACK = auto()


class Star(StringSearchableEnum):
    SUN = auto()
    MOON = auto()
    VENUS = auto()
    MERCURY = auto()

    MARS = auto()
    JUPITER = auto()
    SATURN = auto()
    URANUS = auto()
    PLUTO = auto()
    NEPTUNE = auto()

    __star_advantage_over: dict[Star, Star] = {
        SUN: MOON,
        MOON: VENUS,
        VENUS: MERCURY,
        MERCURY: SUN,

        MARS: JUPITER,
        JUPITER: SATURN,
        SATURN: URANUS,
        URANUS: PLUTO,
        PLUTO: NEPTUNE,
        NEPTUNE: MARS,
    }

    def has_advantage_over(self, other: Star):
        return Star.__star_advantage_over[self] == other


class Face(StringSearchableEnum):
    DOWN = auto()
    UP = auto()


class IsActive(StrEnum):
    DARKEN = auto()


class Card:
    __DEFAULT_BATTLE_MODE = BattleMode.ATTACK
    __DEFAULT_FACE = Face.UP
    __DEFAULT_IS_ACTIVE = True
    __DEFAULT_EQUIP_STAGE = 0

    @staticmethod
    def apply_mods_stat(stat: Stat, type_: Type, field: Field, equip_stage: EquipStage = __DEFAULT_EQUIP_STAGE) \
            -> Stat:
        result = stat
        result += 500 * is_boosted_by(type_, field)
        result -= 500 * is_nerfed_by(type_, field)
        result += 500 * equip_stage
        # result += 500 * (equip_stage or 0)  # TODO: restore default value of 0 if None ?
        # result = min(max(result, 0), 9_999)  # TODO: don't forget to cap during damage calculation

        return result

    def __init__(self, cur: Cursor, id_: Id, field: Field,
                 /,
                 pos: Position = None, equip_stage: EquipStage = None,
                 star: Star = None, battle_mode: BattleMode = None, face: Face = None,
                 is_active: bool = None) \
            -> None:
        try:
            name, star1, star2, type_str, attack, defense = cur.execute(
                f"SELECT CardName, GuardianStar1, GuardianStar2, CardType, Attack, Defense "
                f"FROM Cards "
                f"WHERE CardID = ?",
                (id_,)
            ).fetchone()
        except Exception as e:
            e.add_note(f"Invalid card id {repr(id_)}.")
            raise e
        else:
            self.name: str = name
            self.id: Id = id_
            self.type: Type = Type(type_str)
            is_monster_ = is_monster(self.type)
            self.base_attack: Stat = attack if is_monster_ else None
            self.base_defense: Stat = defense if is_monster_ else None
            self.possible_stars: list[Star] = [Star.by_name(star1), Star.by_name(star2)] if is_monster_ else None
            self._field = field

            self.star: Star = (star or self.possible_stars[0]) if is_monster_ else None
            if is_monster_ and self.star not in self.possible_stars:
                raise ValueError(f'Invalid star {repr(star)}. Expected: {self.possible_stars}')

            self.battle_mode: BattleMode | Literal = battle_mode or Card.__DEFAULT_BATTLE_MODE
            self.face: Face | Literal = face or Card.__DEFAULT_FACE

            self.is_active: bool = is_active if is_active is not None else Card.__DEFAULT_IS_ACTIVE
            self.pos: Position = pos

            self.base_attack_plus_field: Stat | None = None
            self.base_defense_plus_field: Stat | None = None
            self.true_attack: Stat | None = None
            self.true_defense: Stat | None = None
            self._equip_stage: EquipStage | None = (
                equip_stage if equip_stage is not None else Card.__DEFAULT_EQUIP_STAGE
            ) if is_monster_ else None

            self.__update_stats()

    def __repr__(self) -> str:
        # return self.name
        return (
            f'{self.name=} '
            # self.id: Id = id_
            # self.type: Type = Type(type_str)
            # is_monster_ = is_monster(self.type)
            # self.base_attack: Stat = attack if is_monster_ else None
            # self.base_defense: Stat = defense if is_monster_ else None
            # self.possible_stars: list[Star] = [star1, star2] if is_monster_ else None
            # self._field = field

            f'{self.star=} '
            f'{self.battle_mode=} '
            f'{self.face=} '

            f'{self.is_active=} '
            f'{self.pos=} '

            # self.base_attack_plus_field: Stat | None = None
            # self.base_defense_plus_field: Stat | None = None
            # self.true_attack: Stat | None = None
            # self.true_defense: Stat | None = None
            f'{self._equip_stage=} '
        )

    @property
    def star(self) -> Star:
        return self._star

    @star.setter
    def star(self, star: Star) -> None:
        self._star = star

    @property
    def battle_mode(self) -> BattleMode:
        return self._battle_mode

    @battle_mode.setter
    def battle_mode(self, battle_mode: BattleMode) -> None:
        self._battle_mode = battle_mode

    @property
    def face(self) -> Face:
        return self._face

    @face.setter
    def face(self, face: Face) -> None:
        self._face = face

    @property
    def equip_stage(self) -> EquipStage:
        return self._equip_stage

    @equip_stage.setter
    def equip_stage(self, equip_stage: EquipStage) -> None:
        self._equip_stage = equip_stage
        self.__update_stats()

    @property
    def field(self) -> Field:
        return self._field

    @field.setter
    def field(self, field: Field) -> None:
        self._field = field
        self.__update_stats()

    def __update_stats(self):
        if is_monster(self.type):
            self.base_attack_plus_field: Stat = Card.apply_mods_stat(self.base_attack, self.type, field=self.field)
            self.base_defense_plus_field: Stat = Card.apply_mods_stat(self.base_defense, self.type, field=self.field)
            self.true_attack: Stat \
                = Card.apply_mods_stat(self.base_attack, self.type, field=self.field, equip_stage=self.equip_stage)
            self.true_defense: Stat \
                = Card.apply_mods_stat(self.base_defense, self.type, field=self.field, equip_stage=self.equip_stage)

    @property
    def max_base_stat(self) -> Stat:
        return max(self.base_attack, self.base_defense) \
            if is_monster(self.type) \
            else None

    @property
    def max_base_stat_plus_field(self) -> Stat:
        return max(self.base_attack_plus_field, self.base_defense_plus_field) \
            if is_monster(self.type) \
            else None

    @property
    def true_max_stat(self) -> Stat:
        return max(self.true_attack, self.true_defense) \
            if is_monster(self.type) \
            else None

    @override
    def __eq__(self, other):
        if id(self) == id(other):
            return True

        if not isinstance(other, Card):
            return False

        # vars_ = {*vars(self), *vars(other)}
        # for attr in vars_:
        #     if getattr(self, attr) != getattr(other, attr):
        #         return False
        # return True

        return (  # TODO: is there a way to automate ? Would it be worth ?
            self.id == other.id
            and self.type == other.type
            and self.base_attack == other.base_attack
            and self.base_defense == other.base_defense
            and self.possible_stars == other.possible_stars
            # and self.field == other.field
            and self.star == other.star
            and self.battle_mode == other.battle_mode
            and self.face == other.face
            and self.is_active == other.is_active
            and self.pos == other.pos
            and self.equip_stage == other.equip_stage
            # and self.base_attack_plus_field == other.base_attack_plus_field
            # and self.base_defense_plus_field == other.base_defense_plus_field
            # and self.true_attack == other.true_attack
            # and self.true_defense == other.true_defense
        )


class Cards(list[Card | None]):
    def __init__(self, mode: Position.Mode):
        super().__init__()
        self.mode = mode

    @override
    def __getitem__(self, item: Position | slice) -> Iterable[Card] | Card | None:
        # def __getitem__(self, item: Position) -> Card | None:
        if isinstance(item, slice):
            return super().__getitem__(item)  # TODO: check more carefully ?

        elif isinstance(item, Position):
            # if isinstance(item, Position):
            if self.mode != item.mode:
                raise ValueError(f'Trying to access {self.mode} {self.__class__} with a {item.mode} position.')
            return super().__getitem__(item.idx)

        else:
            raise RuntimeError(f'Trying to access {self.__class__} content '
                               f'with unsupported {item} of type {type(item)}.')

    @override
    def __setitem__(self, position_: Position | slice, card_: Iterable[Card] | Card | None):
        if isinstance(position_, slice) and isinstance(card_, Iterable):
            return super().__setitem__(position_, card_)  # TODO: check more carefully ?

        elif isinstance(position_, Position) and isinstance(card_, Card | None):
            # if isinstance(item, Position):
            if self.mode != position_.mode:
                raise ValueError(f'Trying to access {self.mode} {self.__class__} with a {position_.mode} position.')
            return super().__setitem__(position_.idx, card_)

        else:
            raise RuntimeError(f'Trying to access {self.__class__} content '
                               f'with unsupported {position_} of type {type(position_)} '
                               f'or content {card_} of type {type(card_)}.')

    @override
    def __eq__(self, other):
        if id(self) == id(other):
            return True

        if not isinstance(other, Cards):
            return False

        return all(s_card == o_card for (s_card, o_card) in zip(self, other))


class Opponent:
    MIN_LP, MAX_LP = 0, 8_000
    __DEFAULT_LP = MAX_LP

    MIN_TURN = 1
    __DEFAULT_TURN = MIN_TURN

    MIN_REMAINING_TURNS_UNDER_SWORDS, MAX_REMAINING_TURNS_UNDER_SWORDS = 0, 5
    __DEFAULT_REMAINING_TURNS_UNDER_SWORDS = MIN_REMAINING_TURNS_UNDER_SWORDS

    class Type(StrEnum):
        PLAYER = "Player",
        AI = "AI"

    def __init__(self, name: str, type_: str, frontrow: Cards, backrow: Cards, hand: Cards, remaining_deck: Cards,
                 lp: int = None, current_turn: int = None, remaining_turns_under_swords: int = None)\
            -> None:
        self.name: str = name
        self.type: Opponent.Type = Opponent.Type(type_)
        self.frontrow: Cards = frontrow
        self.backrow: Cards = backrow
        self.hand: Cards = hand
        self.remaining_deck: Cards = remaining_deck

        self.lp: int = lp if lp is not None else Opponent.__DEFAULT_LP
        self.current_turn: int = current_turn if current_turn is not None else Opponent.__DEFAULT_TURN
        self.remaining_turns_under_swords: int = (remaining_turns_under_swords
                                                  if remaining_turns_under_swords is not None
                                                  else Opponent.__DEFAULT_REMAINING_TURNS_UNDER_SWORDS)

    @override
    def __eq__(self, other):
        if id(self) == id(other):
            return True

        if not isinstance(other, Opponent):
            return False

        vars_ = {*vars(self), *vars(other)}
        for attr in vars_:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

        # return all(getattr(self, attr) == getattr(other, attr) for attr in vars(self))

        # return (
        #     self.name == other.name
        #     and self.type == other.type
        #     and self.frontrow == other.frontrow
        #     and self.backrow == other.backrow
        #     and self.hand == other.hand
        #     and self.remaining_deck == other.remaining_deck
        #
        #     and self.lp == other.lp
        #     and self.current_turn == other.current_turn
        #     and self.remaining_turns_under_swords == other.remaining_turns_under_swords
        # )

    @override
    def __repr__(self):
        return (
            f'{self.name=} '
            # self.type: Opponent.Type = Opponent.Type(type_)
            f'{self.frontrow=} '
            f'{self.backrow=} '
            f'{self.hand=} '
            f'{self.remaining_deck=} '
            f'{self.lp=}/{Opponent.__DEFAULT_LP} '
            f'{self.current_turn=} '
            f'{self.remaining_turns_under_swords=}'
        )

    def __getitem__(self, item):
        if not isinstance(item, Position):
            raise TypeError(f'Expected {Position}, received {type(item)}.')

        if item.mode == Position.Mode.FRONTROW:
            return self.frontrow[item]
        elif item.mode == Position.Mode.BACKROW:
            return self.backrow[item]
        elif item.mode == Position.Mode.HAND:
            return self.hand[item]
        elif item.mode == Position.Mode.DECK:
            return self.remaining_deck[item]
        else:
            raise RuntimeError(f'Invalid {Position.Mode} {item.mode}.')

    def __setitem__(self, key, value):
        if not isinstance(key, Position):
            raise TypeError(f'Expected {Position}, received {type(key)}.')

        if key.mode == Position.Mode.FRONTROW:
            self.frontrow[key] = value
        elif key.mode == Position.Mode.BACKROW:
            self.backrow[key] = value
        elif key.mode == Position.Mode.HAND:
            self.hand[key] = value
        elif key.mode == Position.Mode.DECK:
            self.remaining_deck[key] = value
        else:
            raise RuntimeError(f'Invalid {Position.Mode} {key.mode}.')

    @property
    def lp(self):
        return self._lp

    @lp.setter
    def lp(self, lp):
        self._lp = min(max(lp, Opponent.MIN_LP), Opponent.MAX_LP)


# class EndOfTurnType:
#     pass
#
#
# EndOfTurn = EndOfTurnType()
#
#
# def raise_no_other_instance_error() -> None:
#     raise RuntimeError(f"Can't instantiate another {EndOfTurnType} instance.")
#
#
# EndOfTurnType.__init__ = raise_no_other_instance_error

class EndOfTurnType(Enum):
    token = 0


EndOfTurn = EndOfTurnType.token
