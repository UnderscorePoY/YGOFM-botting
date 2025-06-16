from __future__ import annotations
import math
from copy import deepcopy
from typing import Any, Iterator

from types_ import Position


class Odds:
    def __init__(self, odds: tuple[int, int]) \
            -> None:
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
    def validate(odds: tuple[int, int]) -> None:
        num, denom = odds
        assert 0 <= num <= denom and denom > 0  # TODO: assert can be skipped ?

    def complementary(self) -> Odds:
        return Odds((self.denom - self.num, self.denom))

    def __repr__(self) -> str:
        return '/'.join([str(i) for i in self.simplified_odds]) if self.odds[0] > 0 else ''

    def __eq__(self, other) -> bool:
        if id(self) == id(other):
            return True

        if not isinstance(other, Odds):
            return False

        return self.simplified_odds == other.simplified_odds


class Action:
    """ An action that can be applied to a `GameState`, consisting of a description,
    the odds for this action to be chosen and the next action/state. """
    BASE_LEVEL = 1
    DEFAULT_ODDS = (1, 1)

    class Description:
        def __init__(self, source: Position | None, action: Any, target: Position = None)\
                -> None:  # TODO: specify possible action types instead of Any ?
            self.source = source
            self.action = action
            self.target = target

        @classmethod
        def from_tuple(cls, description: tuple) -> Action.Description:
            source, action, *target = description
            target, = target if target else (None,)
            return cls(source, action, target)

        def __eq__(self, other) -> bool:
            if id(self) == id(other):
                return True

            if isinstance(other, tuple):
                return self == Action.Description.from_tuple(other)
            elif isinstance(other, Action.Description):
                return (self.source == other.source
                        and self.action == other.action
                        and self.target == other.target)

            return False

        def __repr__(self):
            return "%s -> %s%s" % (self.source, self.action, f' -> {self.target}' if self.target else '')

    def __init__(self, descriptions: list[Description] = None,
                 odds: Odds | tuple[int, int] = None,
                 next_: Actions | GameState | list[Action] = None,
                 level: int = BASE_LEVEL) \
            -> None:
        self.level = level
        self.descriptions = descriptions
        self.odds = odds
        self.next: Actions | GameState

        if next_ is None:
            self.next = Actions(next_, level=level + 1)
        elif isinstance(next_, GameState):
            next_.level = level
            self.next = next_
        elif isinstance(next_, Actions):
            next_.level = level
            if len(next_) == 1 and self.descriptions is None:  # TODO: fix this
                self.descriptions = next_.actions[0].descriptions
                self.next = Actions(None, level=level+1)
            else:
                self.next = next_
        elif is_iterable(next_):
            if len(next_) == 1 and self.descriptions is None:  # TODO: fix this
                self.descriptions = next_[0].descriptions
                self.next = Actions(None, level=level+1)
            else:
                self.next = Actions(next_, level=level + 1)
        else:
            raise ValueError(f"Unsupported attribute {repr(next_)} of type {repr(type(next_))}.")

    @property
    def descriptions(self) -> list[Description]:
        return self._descriptions

    @descriptions.setter
    def descriptions(self, descriptions: list[Description]) -> None:
        self._descriptions = descriptions  # if desc is not None else []  # TODO: add default empty list ?

    @property
    def odds(self) -> Odds:
        return self._odds

    @odds.setter
    def odds(self, odds: Odds) -> None:
        self._odds = odds if isinstance(odds, Odds) else Odds(odds if odds is not None else Action.DEFAULT_ODDS)

    def __repr__(self) -> str:
        sep = '\n' + '\t' * self.level + '└> '

        return (
            sep + repr(self.odds) + ": " + repr(self.descriptions)
            + repr(self.next)
        )

    def __eq__(self, other) -> bool:
        if id(self) == id(other):
            return True

        if not isinstance(other, Action):
            return False

        return self.descriptions == other.descriptions \
            and self.odds == other.odds \
            and self.next == other.next

    def append_horizontally(self, actions: list[Action]) \
            -> None:
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

    def append_deepest_horizontally(self, actions: list[Action], level: int = BASE_LEVEL)\
            -> None:
        r""" Appends `actions` horizontally to all the deepest successors of this action.
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
    def __init__(self, actions: list[Action] = None, level: int = None)\
            -> None:
        self.actions: list[Action] = []
        if actions is not None:
            self.append_horizontally(actions=actions, level=level)

    def append(self, action: Action, level: int = Action.BASE_LEVEL, new_objects: bool = False) \
            -> None:
        new_action = deepcopy(action) if new_objects else action
        if level is not None:
            new_action.level = level
        elif len(self.actions) > 0:
            new_action.level = self.actions[0].level
        else:
            new_action.level = Action.BASE_LEVEL
        self.actions.append(new_action)

    def append_horizontally(self, actions: list[Action], level: int = Action.BASE_LEVEL)\
            -> None:
        for action in actions:
            self.append(action, level=level, new_objects=False)

    def append_deepest_horizontally(self, actions: list[Action], level: int = Action.BASE_LEVEL)\
            -> None:
        if len(self.actions) == 0:
            self.append_horizontally(actions)
            return

        for action in self.actions:
            action.append_deepest_horizontally(actions, level=level+1 if level is not None else level)

    def __iter__(self) -> Iterator[Action]:
        return self.actions.__iter__()

    def __len__(self) -> int:
        return self.actions.__len__()

    def __eq__(self, other) -> bool:
        if id(self) == id(other):
            return True

        if not isinstance(other, Actions):
            return False

        return all((s == o for (s, o) in zip(self.actions, other.actions)))

    def __repr__(self) -> str:
        return ''.join((repr(action) for action in self.actions))


class GameState:
    """ A tree structure holding a current game state and the list of disjoint actions that can be applied to it. """
    # TODO : do we actually ever use a GameState anywhere ?

    def __init__(self, player, ai_player, field, next_: list[Action] = None, level: int = 0)\
            -> None:
        self.player = deepcopy(player)
        self.ai_player = deepcopy(ai_player)
        self.field = deepcopy(field)

        self.__level = level
        self.next = Actions(next_, level=level + 1)

    def __len__(self) -> int:
        return self.next.__len__()

    def __repr__(self) -> str:
        leads_to = ' -> '
        return (
            leads_to
            + ', '.join(['Player: ' + repr(self.player), 'AI: ' + repr(self.ai_player), 'Field: ' + repr(self.field)])
            + ''.join([repr(action) for action in self.next]) if self.next is not None else ''
        )

    def append_deepest_horizontally(self, actions: list[Action], level: int = 0)\
            -> None:
        self.next.append_deepest_horizontally(actions, level=level+1)


def is_iterable(obj: Any) -> bool:
    try:
        _ = iter(obj)
    except TypeError:
        return False
    else:
        return True


# def test_tree():  # TODO
#     gs = GameState('pl1', 'ai1', 'f1', next_=[
#         Action('Action 1', (50, 100), [
#             Action('Action 1.1', (75, 100), GameState('pl1.1', 'ai1.1', 'f1.1')),
#             Action('Action 1.2', (25, 100), GameState('pl1.2', 'ai1.2', 'f1.2'))
#         ]),
#         Action('Action 2', (40, 100), GameState('pl2', 'ai2', 'f2')),
#         Action('Action 3', (10, 100), GameState('pl3', 'ai3', 'f3'))
#     ])
#
#     print(gs)
#
#     appendee = [
#         Action('Action 4.1', (75, 100), GameState('pl4.1', 'ai4.1', 'f4.1')),
#         Action('Action 4.2', (25, 100), GameState('pl4.2', 'ai4.2', 'f4.2'))
#     ]
#
#     gs.append_deepest_horizontally(appendee)
#
#     print(gs)
#
#
# if __name__ == '__main__':
#     test_tree()
