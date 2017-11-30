import unittest
from rollout.lib.toposort import toposort


def in_order(items, order):
    assert len(items) == len(order)
    for item, k in zip(items, order):
        assert item['name'] == k
    return True


class TestToposort(unittest.TestCase):
    def test_toposort(self):
        items = [
            dict(name='one', before=['two']),
            dict(name='two', before=['three']),
            dict(name='three'),
        ]
        items = toposort(items, key=lambda d: d['name'],
                         before=lambda d: d.get('before', []),
                         after=lambda d: d.get('after', []),
                         )
        assert in_order(items, [
            'one',
            'two',
            'three',
        ])

        items = [
            dict(name='two', before=['three']),
            dict(name='three'),
            dict(name='one', before=['two']),
        ]
        items = toposort(items, key=lambda d: d['name'],
                         before=lambda d: d.get('before', []),
                         after=lambda d: d.get('after', []),
                         )
        assert in_order(items, [
            'one',
            'two',
            'three',
        ])

        items = [
            dict(name='three', after=['two']),
            dict(name='one', before=['two']),
            dict(name='two'),
        ]
        items = toposort(items, key=lambda d: d['name'],
                         before=lambda d: d.get('before', []),
                         after=lambda d: d.get('after', []),
                         )
        assert in_order(items, [
            'one',
            'two',
            'three',
        ])

    def test_toposort_failure(self):
        # cycle
        items = [
            dict(name='three', before=['one']),
            dict(name='one', before=['two']),
            dict(name='two', before=['three']),
        ]
        with self.assertRaises(ValueError):
            toposort(items, key=lambda d: d['name'],
                     before=lambda d: d.get('before', []),
                     after=lambda d: d.get('after', []),
                     )

        # before unknown key raises error
        items = [
            dict(name='three', before=['four']),
            dict(name='one', before=['two']),
            dict(name='two', before=['three']),
        ]

        with self.assertRaises(ValueError):
            toposort(items, key=lambda d: d['name'],
                     before=lambda d: d.get('before', []),
                     after=lambda d: d.get('after', []),
                     )

        # after unknown key raises error
        items = [
            dict(name='three', after=['two']),
            dict(name='one', after=['zero']),
            dict(name='two', before=['three']),
        ]

        with self.assertRaises(ValueError):
            toposort(items, key=lambda d: d['name'],
                     before=lambda d: d.get('before', []),
                     after=lambda d: d.get('after', []),
                     )

    def test_toposort_stable(self):
        items = [
            dict(name='three', after=['one']),
            dict(name='two', after=['one']),
            dict(name='one'),
        ]
        items = toposort(items, key=lambda d: d['name'],
                         before=lambda d: d.get('before', []),
                         after=lambda d: d.get('after', []),
                         )
        assert in_order(items, [
            'one',
            'three',
            'two',
        ])

        items = [
            dict(name='two', after=['one']),
            dict(name='three', after=['one']),
            dict(name='one'),
        ]
        items = toposort(items, key=lambda d: d['name'],
                         before=lambda d: d.get('before', []),
                         after=lambda d: d.get('after', []),
                         )
        assert in_order(items, [
            'one',
            'two',
            'three',
        ])
