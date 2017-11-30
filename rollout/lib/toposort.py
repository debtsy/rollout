from typing import Callable, Optional, Iterable
from collections import defaultdict

OptCallable = Optional[Callable]


class KeyedIndexList:
    def __init__(self, key):
        self.data = []
        self.index_lookup = {}
        self.key = key

    def insert(self, idx, item):
        self.data.insert(idx, item)
        self.index_lookup = {self.key(item): i for i, item in enumerate(self.data)}

    def __contains__(self, k):
        return k in self.index_lookup

    def __getitem__(self, k):
        return self.index_lookup[k]

    def __len__(self):
        return len(self.data)


# Take an list of Rules. if

def topo_insert(k, items, key, before, after, new_order, after_inverted):
    if k is None:
        idx = 0
    else:
        idx = None
        for i, candidate_item in enumerate(items):
            if k == key(candidate_item):
                idx = i
                break
        if idx is None:
            raise ValueError(f'Dependency {k} not found in list. It might have caused a cycle.')
    item = items.pop(idx)
    k = key(item)

    if before:
        before_keys = before(item) + after_inverted[k]
        for before_key in before_keys:
            if before_key not in new_order:
                # note these lines change len(new_order)
                new_order = topo_insert(before_key, items, key, before, after, new_order, after_inverted)

        placement_index = len(new_order)
        for before_key in before_keys:
            placement_index = min(placement_index, new_order[before_key])
    else:
        placement_index = len(new_order)

    if after:
        after_keys = after(item)

        for after_key in after_keys:
            after_inverted[after_key].append(k)

    new_order.insert(placement_index, item)
    return new_order


def toposort(items: list, key: Callable, before: OptCallable = None, after: OptCallable = None) -> list:
    new_order = KeyedIndexList(key)
    after_inverted = defaultdict(list)
    while items:
        new_order = topo_insert(None, items, key, before, after, new_order, after_inverted)

    for k in after_inverted:
        if k not in new_order:
            raise ValueError(f'Dependency {k} was not found.')

    return new_order.data


def rule_toposort(rules):
    def key(rule):
        return rule.name

    def before(rule):
        return rule.before or []

    def after(rule):
        return rule.after or []

    return toposort(rules, key, before=before, after=after)
