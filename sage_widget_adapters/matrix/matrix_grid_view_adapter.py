# -*- coding: utf-8 -*-
r"""
Grid View Adapter for matrices

**Grid View matrix operations:**

.. csv-table::
    :class: contentstable
    :widths: 30, 70
    :delim: |

    :meth:`~TableauGridViewAdapter.cell_to_unicode` | Static method for typecasting cell content to unicode
    :meth:`~TableauGridViewAdapter.unicode_to_cell` | Static method for typecasting unicode to cell content
    :meth:`~MatrixGridViewAdapter.compute_cells` | Compute matrix cells as a dictionary { coordinate pair : label }
    :meth:`~MatrixGridViewAdapter.from_cells` | Create a new matrix from a cells dictionary
    :meth:`~MatrixGridViewAdapter.get_cell` | Get the matrix cell value
    :meth:`~MatrixGridViewAdapter.set_cell` | Set the matrix cell value
    :meth:`~MatrixGridViewAdapter.addable_cells` | List addable cells
    :meth:`~MatrixGridViewAdapter.removable_cells` | List removable cells
    :meth:`~MatrixGridViewAdapter.add_cell` | Add a cell
    :meth:`~MatrixGridViewAdapter.remove_cell` | Remove a cell
    :meth:`~MatrixGridViewAdapter.append_row` | Append a row
    :meth:`~MatrixGridViewAdapter.insert_row` | Insert a row at given index
    :meth:`~MatrixGridViewAdapter.remove_row` | Remove a row at given index
    :meth:`~MatrixGridViewAdapter.append_column` | Append a column
    :meth:`~MatrixGridViewAdapter.insert_column` | Insert a column at given index
    :meth:`~MatrixGridViewAdapter.remove_column` | Remove a column at given index
"""
from sage.matrix.matrix2 import Matrix as MatrixClass
from sage.matrix.constructor import Matrix
from sage_widget_adapters.generic_grid_view_adapter import GridViewAdapter

class MatrixGridViewAdapter(GridViewAdapter):
    objclass = MatrixClass

    @staticmethod
    def cell_to_unicode(cell_content):
        return str(cell_content)

    @staticmethod
    def unicode_to_cell(s):
        if obj.base_ring().is_subring(ZZ):
            return ZZ(s)
        if obj.base_ring().is_subring(QQ):
            return QQ(float(s))
        if obj.base_ring().is_subring(RDF):
            return RDF(s)
        if obj.base_ring().is_subring(CDF):
            return CDF(s)
        try:
            return obj.base_ring()(s)
        except:
            try:
                return obj.base_ring()(float(s))
            except:
                raise TypeError("Unable to cast this value: %s" % s)

    @staticmethod
    def compute_cells(obj):
        r"""
        From a tableau,
        return a dictionary { coordinates pair : integer }
        """
        cells = {}
        for i in obj.numrows():
            r = obj[i]
            for j in obj.numcols():
                cells[(i,j)] = r[j]
        return cells

    @classmethod
    def from_cells(cls, cells={}):
        rows = []
        i = 0
        while i < max(pos[0] for pos in cells):
            row = (cells[pos] for pos in cells if pos[0] == i)
            rows.append(row)
            i += 1
        return matrix(rows)

    @staticmethod
    def get_cell(obj, pos):
        r"""
        Get cell content
        """
        if pos[0] >= obj.nrows() or pos[1] >= obj.ncols():
            raise ValueError("Entry '%s' does not exist!" % pos)
        return obj[pos[0]][pos[1]]

    @classmethod
    def set_cell(cls, obj, pos, val):
        r"""
        Edit matrix cell
        TESTS::
        sage: from sage.matrix.constructor import Matrix
        sage: from sage_widget_adapters.matrix.matrix_grid_view_adapter import MatrixGridViewAdapter
        sage: A = Matrix(QQ, 3, 3, range(9))/2
        sage: MatrixGridViewAdapter.set_cell(A, (0,1), 2/3)
        [  0 2/3   1]
        [3/2   2 5/2]
        [  3 7/2   4]
        sage: MatrixGridViewAdapter.set_cell(A, (2,2), pi) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        TypeError: Value 'pi' is not compatible!
        """
        if not val in obj.base_ring():
            raise TypeError("Value '%s' is not compatible!" % val)
        B = Matrix(obj.base_ring(), 1, 1, val)
        obj.set_block(pos[0], pos[1], B)
        return obj

    @staticmethod
    def addable_cells(obj):
        r"""
        No cell should be added in isolation
        except for vectors
        """
        if obj.nrows() == 1:
            return [(0, obj.ncols())]
        if obj.ncols() == 1:
            return [(obj.nrows(), 0)]
        return []

    @staticmethod
    def removable_cells(obj):
        r"""
        No cell should be removed in isolation
        except for vectors
        """
        if obj.nrows() == 1:
            return [(0, obj.ncols()-1)]
        if obj.ncols() == 1:
            return [(obj.nrows()-1, 0)]
        return []

    @classmethod
    def add_cell(cls, obj, pos, val):
        r"""
        No cell should be added in isolation
        except for vectors
        """
        if not pos in obj.addable_cells():
            raise ValueError("Position '%s' is not addable." % str(pos))
        if pos[0] == 0:
            return obj.augment(vector([val]))
        if pos[1] == 0:
            return obj.stack(vector([val]))

    @classmethod
    def remove_cell(cls, obj, pos):
        r"""
        No cell should be removed in isolation
        except for vectors
        """
        if not pos in obj.removable_cells():
            return obj
        if pos[0] == 0:
            return obj.matrix_from_columns(range(obj.ncols()-1))
        if pos[1] == 1:
            return obj.matrix_from_rows(range(obj.nrows()-1))

    @classmethod
    def append_row(cls, obj, r=None):
        r"""
        """
        if not r:
            return obj.stack(vector([0] * obj.ncols()))
        for x in r:
            if not x in obj.base_ring():
                raise TypeError("Value '%s' is not compatible!" % x)
        if len(r) > obj.ncols():
            r = c[obj.ncols()]
        elif len(r) < obj.ncols():
            r = r + [0] * (obj.ncols() - len(r))
        return obj.stack(vector(r))

    @classmethod
    def insert_row(cls, obj, index, r=None):
        r"""
        """
        if not r:
            r = [0] * obj.ncols()
        else:
            for x in r:
                if not x in obj.base_ring():
                    raise TypeError("Value '%s' is not compatible!" % x)
            if len(r) > obj.ncols():
                r = c[obj.ncols()]
            elif len(r) < obj.ncols():
                r = r + [0] * (obj.ncols() - len(r))
        top = obj.matrix_from_rows(range(index))
        bottom = obj.matrix_from_rows(range(index,obj.nrows()))
        return top.stack(vector(r)).stack(bottom)

    @classmethod
    def remove_row(cls, obj, index=None):
        r"""
        TESTS::
        sage: from sage.matrix.matrix_space import MatrixSpace
        sage: S = MatrixSpace(ZZ, 4,3)
        sage: from sage_widget_adapters.matrix.matrix_grid_view_adapter import MatrixGridViewAdapter
        sage: A = S.matrix([0,1,2,3,4,5,6,7,8,9,10,11])
        sage: MatrixGridViewAdapter.remove_row(A, 2)
        [ 0  1  2]
        [ 3  4  5]
        [ 9 10 11]
        sage: MatrixGridViewAdapter.remove_row(A)
        [0 1 2]
        [3 4 5]
        [6 7 8]
        """
        if index is None:
            index = obj.nrows() - 1
        return obj.delete_rows([index])

    @classmethod
    def append_column(cls, obj, c = None):
        r"""
        """
        if not c:
            obj.augment(vector([0]*obj.nrows()))
        for x in c:
            if not x in obj.base_ring():
                raise TypeError("Value '%s' is not compatible!" % x)
        if len(c) > obj.nrows():
            c = c[obj.nrows()]
        elif len(c) < obj.nrows():
            c = c + [0] * (obj.nrows() - len(c))
        return obj.augment(vector(c))

    @classmethod
    def insert_column(cls, obj, index, c=None):
        r"""
        """
        if not c:
            c = [0] * obj.nrows()
        else:
            for x in c:
                if not x in obj.base_ring():
                    raise TypeError("Value '%s' is not compatible!" % x)
            if len(c) > obj.nrows():
                c = c[obj.nrows()]
            elif len(c) < obj.nrows():
                c = c + [0] * (obj.nrows() - len(c))
        left = obj.matrix_from_columns(range(index))
        right = obj.matrix_from_columns(range(index,obj.nrows()))
        return left.stack(vector(c)).stack(right)

    @classmethod
    def remove_column(cls, obj, index=None):
        r"""
        TESTS::
        sage: from sage.matrix.matrix_space import MatrixSpace
        sage: S = MatrixSpace(ZZ, 4,3)
        sage: from sage_widget_adapters.matrix.matrix_grid_view_adapter import MatrixGridViewAdapter
        sage: A = S.matrix([0,1,2,3,4,5,6,7,8,9,10,11])
        sage: MatrixGridViewAdapter.remove_column(A, 1)
        [ 0  2]
        [ 3  5]
        [ 6  8]
        [ 9 11]
        sage: MatrixGridViewAdapter.remove_column(A)
        [ 0  1]
        [ 3  4]
        [ 6  7]
        [ 9 10]
        """
        if index is None:
            index = obj.ncols() - 1
        return obj.delete_columns([index])
