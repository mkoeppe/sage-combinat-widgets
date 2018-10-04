# -*- coding: utf-8 -*-
r"""
Grid View Adapter for tableaux

**Grid View tableau operations:**

.. csv-table::
    :class: contentstable
    :widths: 30, 70
    :delim: |

    :meth:`~TableauGridViewAdapter.unicode_to_cell` | Static method for typecasting unicode to cell content
    :meth:`~TableauGridViewAdapter.compute_cells` | Compute tableau cells as a dictionary { coordinate pair : integer }
    :meth:`~TableauGridViewAdapter.from_cells` | Create a new tableau from a cells dictionary
    :meth:`~TableauGridViewAdapter.get_cell` | Get the tableau cell content
    :meth:`~TableauGridViewAdapter.set_cell` | Set the tableau cell content
    :meth:`~TableauGridViewAdapter.addable_cells` | List addable cells
    :meth:`~TableauGridViewAdapter.removable_cells` | List removable cells
    :meth:`~TableauGridViewAdapter.add_cell` | Add a cell
    :meth:`~TableauGridViewAdapter.remove_cell` | Remove a cell
"""
from sage.combinat.tableau import *
from sage.rings.integer import Integer
from traitlets import Int
from sage_widget_adapters.generic_grid_view_adapter import GridViewAdapter

class TableauGridViewAdapter(GridViewAdapter):
    objclass = Tableau
    traitclass = Int

    @staticmethod
    def unicode_to_cell(s):
        return int(s)

    @staticmethod
    def compute_cells(obj):
        r"""
        From a tableau,
        return a dictionary { coordinates pair : integer }
        TESTS:
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3], [4]])
        sage: TableauGridViewAdapter.compute_cells(t)
        {(0, 0): 1, (0, 1): 2, (0, 2): 5, (0, 3): 6, (1, 0): 3, (2, 0): 4}
        """
        cells = {}
        for i in range(len(obj)):
            r = obj[i]
            for j in range(len(r)):
                cells[(i,j)] = int(r[j])
        return cells

    @classmethod
    def from_cells(cls, cells={}):
        r"""
        From a dictionary { coordinates pair : integer }
        return a corresponding tableau
        TESTS:
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: TableauGridViewAdapter.from_cells({(0, 0): 1, (0, 1): 2, (0, 2): 5, (0, 3): 6, (1, 0): 3, (2, 0): 4})
        [[1, 2, 5, 6], [3], [4]]
        """
        rows = []
        i = 0
        while i <= max(pos[0] for pos in cells):
            row = [cells[pos] for pos in cells if pos[0] == i]
            row.sort()
            rows.append(row)
            i += 1
        try:
            obj = cls.objclass(rows)
        except:
            raise TypeError("This object is not compatible with this adapter (%s, for %s objects)" % (cls, cls.objclass))
        return obj

    @staticmethod
    def get_cell(obj, pos):
        r"""
        Get cell value
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.get_cell(t, (1,1))
        7
        """
        try:
            return obj.__call__(pos)
        except:
            raise ValueError("Cell %s does not exist!" % str(pos))

    @classmethod
    def set_cell(cls, obj, pos, val):
        r"""
        Set cell value
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.set_cell(t, (1,1), 8)
        [[1, 2, 5, 6], [3, 8], [4]]
        """
        tl = obj.to_list()
        nl = []
        for i in range(len(tl)):
            l = tl[i]
            if i == pos[0]:
                l[pos[1]] = val
            nl.append(l)
        try:
            new_obj = cls.objclass(nl)
        except:
            raise ValueError("Value '%s' is not compatible!" % val)
        else:
            return new_obj

    @staticmethod
    def addable_cells(obj):
        r"""
        List object addable cells
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.addable_cells(t)
        [(0, 4), (1, 2), (2, 1), (3, 0)]
        """
        return obj.shape().outside_corners()

    @staticmethod
    def removable_cells(obj):
        r"""
        List object removable cells
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.removable_cells(t)
        [(0, 3), (1, 1), (2, 0)]
        """
        return obj.corners()

    @classmethod
    def add_cell(cls, obj, pos, val):
        r"""
        Add cell
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.add_cell(t, (3, 0), 8)
        [[1, 2, 5, 6], [3, 7], [4], [8]]
        sage: TableauGridViewAdapter.add_cell(t, (1, 2), 8)
        [[1, 2, 5, 6], [3, 7, 8], [4]]
        sage: TableauGridViewAdapter.add_cell(t, (2, 0), 9) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: Cell position '(2, 0)' is not addable.
        """
        if not pos in cls.addable_cells(obj):
            raise ValueError("Position '%s' is not addable." % str(pos))
        tl = obj.to_list()
        if pos[0] >= len(tl):
            nl = tl + [[Integer(val)]]
        else:
            nl = []
            for i in range(len(tl)):
                l = tl[i]
                if i == pos[0]:
                    l.append(Integer(val))
                nl.append(l)
        try:
            new_obj = cls.objclass(nl)
        except:
            raise ValueError("Cannot create a %s with this list!" % cls.objclass)
        else:
            return new_obj

    @classmethod
    def remove_cell(cls, obj, pos):
        r"""
        Remove cell
        TESTS::
        sage: from sage.combinat.tableau import Tableau
        sage: from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        sage: t = Tableau([[1, 2, 5, 6], [3, 7], [4]])
        sage: TableauGridViewAdapter.remove_cell(t, (1, 1))
        [[1, 2, 5, 6], [3], [4]]
        sage: TableauGridViewAdapter.remove_cell(t, (2, 1)) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: Cell position '(2, 1)' is not removable.
        """
        if not pos in cls.removable_cells(obj):
            raise ValueError("Cell position '%s' is not removable." % str(pos))
        tl = obj.to_list()
        nl = []
        for i in range(len(tl)):
            l = tl[i]
            if i == pos[0]:
                l.pop()
            nl.append(l)
        try:
            new_obj = cls.objclass(nl)
        except:
            raise ValueError("Cannot create a %s with this list!" % cls.objclass)
        else:
            return new_obj
