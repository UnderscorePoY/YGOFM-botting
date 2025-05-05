from __future__ import annotations
import math
from copy import deepcopy
from typing import Union, Any


class Odds:
    def __init__(self, odds: tuple[int, int]) -> None:
        self.odds = odds
        self.simplified_odds = self.simplified()

    @property
    def odds(self) -> tuple[int, int]:
        return self._odds

    @odds.setter
    def odds(self, odds: tuple[int, int]) -> None:
        Odds.validate(odds)
        self._odds = odds if odds[0] > 0 else (0, 1)

    def simplified(self) -> tuple[int, int]:
        num, denom = self.odds
        gcd = math.gcd(num, denom)
        return num // gcd, denom // gcd

    def approx(self, digits: int = 2) -> str:
        exp = 10 ** digits
        return str(int(exp * 100 * self.num / self.denom) / exp) + '%'

    @property
    def num(self) -> int:
        return self.odds[0]

    @property
    def denom(self) -> int:
        return self.odds[1]

    @staticmethod
    def validate(odds: tuple[int, int]):
        num, denom = odds
        assert 0 <= num <= denom and denom > 0

    def complementary(self) -> Odds:
        return Odds((self.denom - self.num, self.denom))

    def __repr__(self):
        return '/'.join([str(i) for i in self.simplified_odds]) if self.odds[0] > 0 else ''

    def __eq__(self, other):
        if not isinstance(other, Odds):
            return False

        return self.simplified_odds == other.simplified_odds


class Action:
    """ An action that can be applied to a `GameState`, consisting of a description,
    the odds for this action to be chosen and the next action/state. """
    BASE_LEVEL = 1
    DEFAULT_ODDS = (1, 1)

    def __init__(self, description=None, odds: Union[Odds, tuple[int, int]] = None,
                 _next: Union[Actions, GameState, list[Action]] = None, level: int = BASE_LEVEL) -> None:
        self.level = level
        self.description = description
        self.odds = odds
        self.next: Union[Actions, GameState]

        if _next is None:
            self.next = Actions(_next, level=level+1)
        elif isinstance(_next, GameState):
            _next.level = level
            self.next = _next
        elif isinstance(_next, Actions):
            _next.level = level
            if len(_next) == 1 and self.description is None:  # TODO: fix this
                self.description = _next.actions[0].description
                self.next = Actions(None, level=level+1)
            else:
                self.next = _next
        elif is_iterable(_next):
            if len(_next) == 1 and self.description is None:  # TODO: fix this
                self.description = _next[0].description
                self.next = Actions(None, level=level+1)
            else:
                self.next = Actions(_next, level=level+1)
        else:
            raise ValueError(f"Unsupported attribute {repr(_next)} of type {repr(type(_next))}.")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc  # if desc is not None else []  # TODO: add default empty list ?

    @property
    def odds(self):
        return self._odds

    @odds.setter
    def odds(self, odds):
        self._odds = odds if isinstance(odds, Odds) else Odds(odds if odds is not None else Action.DEFAULT_ODDS)

    def __repr__(self):
        sep = '\n' + '\t' * self.level + '└> '
        # if isinstance(self.next, Actions):
        #     str_next = ''.join(repr(n) for n in self.next)
        # else:
        #     str_next = repr(self.next)

        return sep + repr(self.odds) + ": " + repr(self.description) \
               + repr(self.next)  # str_next

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False

        return self.description == other.description \
            and self.odds == other.odds \
            and self.next == other.next

    def append_horizontally(self, actions: list[Action]):
        """ Appends `actions` horizontally to the immediate successors of this action (or the actions
        following a `GameState`).
        Example : if `actions == [b1, b2]` and `self.next == [a1]`, then the result is
        `self.next == [a1, b1, b2]`. """

        if self.next is None:
            self.next = []

        target = self.next.next if isinstance(self.next, GameState) else self.next

        # if is_iterable(target):
        for action in actions:
            target.append(action)
        # else:
        #     raise RuntimeError(f"Can't append horizontally to {repr(target)} of type {type(target)}.")

    def append_deepest_horizontally(self, actions: list[Action], level: int = BASE_LEVEL):
        """ Appends `actions` horizontally to all the deepest successors of this action.
        Example : if `actions == [b1, b2]` and `self.next == [a1, a2]` with `a1.next == []`, `a2.next == [c1]`
        and c1.next == [], then the result is `self.next == [a1, a2]` with `a1.next == [b1, b2]`, `a2.next == [c1]` and
        c1.next == [b1, b2]. Visually :
                        .           .                 .
                       / \         / \               / \
                      a1 a2   +   b1 b2   =        a1   a2
                          \                       / \    \
                          c1                     b1 b2   c1
                                                        / \
                                                       b1 b2
        """

        if self.next is None:
            self.next = []

        if len(self.next) == 0:
            self.next = Actions(actions=actions, level=level)
            return

        target = self.next.next if isinstance(self.next, GameState) else self.next

        for action in target:
            action.append_deepest_horizontally(actions, level+1)

    # def multiply_odds_by(self, odds):
    #     """ Multiplies current odds with the provided `odds`. """
    #     curr_num, curr_denom = self.odds
    #     mult_num, mult_denom = odds
    #     self.odds = curr_num * mult_num, curr_denom * mult_denom


class Actions:
    def __init__(self, actions: list[Action] = None, level: int = None):
        self.actions: list[Action] = []
        if actions is not None:
            self.append_horizontally(actions=actions, level=level)

    def append(self, action: Action, level: int = Action.BASE_LEVEL, new_objects: bool = False) -> None:
        new_action = deepcopy(action) if new_objects else action
        if level is not None:
            new_action.level = level
        elif len(self.actions) > 0:
            new_action.level = self.actions[0].level
        else:
            new_action.level = Action.BASE_LEVEL
        self.actions.append(new_action)

    def append_horizontally(self, actions: list[Action], level: int = Action.BASE_LEVEL):
        for action in actions:
            self.append(action, level=level, new_objects=False)

    def append_deepest_horizontally(self, actions: list[Action], level: int = Action.BASE_LEVEL):
        for action in self.actions:
            action.append_deepest_horizontally(actions, level=level+1 if level is not None else level)

    def __iter__(self):
        return self.actions.__iter__()

    def __len__(self):
        return self.actions.__len__()

    def __eq__(self, other):
        if not isinstance(other, Actions):
            return False

        return all((s == o for (s, o) in zip(self.actions, other.actions)))

    def __repr__(self):
        return ''.join((repr(action) for action in self.actions))


class GameState:
    """ A tree structure holding a current game state and the list of disjoint actions that can be applied to it. """

    def __init__(self, player, ai_player, field, next: list[Action] = None, level: int = 0):
        self.player = deepcopy(player)
        self.ai_player = deepcopy(ai_player)
        self.field = deepcopy(field)

        self.__level = level
        self.next = Actions(next, level=level+1)

    def __len__(self):
        return self.next.__len__()

    def __repr__(self):
        leads_to = ' -> '
        return leads_to \
               + ', '.join(['Player: ' + repr(self.player), 'AI: ' + repr(self.ai_player), 'Field: ' + repr(self.field)]) \
               + ''.join([repr(action) for action in self.next]) \
            if self.next is not None \
            else ''

    def append_deepest_horizontally(self, actions: list[Action], level: int = 0):
        self.next.append_deepest_horizontally(actions, level=level+1)


def is_iterable(obj: Any) -> bool:
    try:
        _ = iter(obj)
    except TypeError:
        return False
    else:
        return True


def test_tree():
    gs = GameState('pl1', 'ai1', 'f1', next=[
        Action('Action 1', (50, 100), [
            Action('Action 1.1', (75, 100), GameState('pl1.1', 'ai1.1', 'f1.1')),
            Action('Action 1.2', (25, 100), GameState('pl1.2', 'ai1.2', 'f1.2'))
        ]),
        Action('Action 2', (40, 100), GameState('pl2', 'ai2', 'f2')),
        Action('Action 3', (10, 100), GameState('pl3', 'ai3', 'f3'))
    ])

    print(gs)

    appendee = [
        Action('Action 4.1', (75, 100), GameState('pl4.1', 'ai4.1', 'f4.1')),
        Action('Action 4.2', (25, 100), GameState('pl4.2', 'ai4.2', 'f4.2'))
    ]

    gs.append_deepest_horizontally(appendee)

    print(gs)


if __name__ == '__main__':
    test_tree()
