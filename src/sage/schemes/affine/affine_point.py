r"""
Points on affine varieties

Scheme morphism for points on affine varieties.


AUTHORS:

- David Kohel, William Stein

- Volker Braun (2011-08-08): Renamed classes, more documentation, misc
  cleanups.

- Ben Hutz (2013)
"""

# Historical note: in trac #11599, V.B. renamed
# * _point_morphism_class -> _morphism
# * _homset_class -> _point_homset

#*****************************************************************************
#       Copyright (C) 2011 Volker Braun <vbraun.name@gmail.com>
#       Copyright (C) 2006 David Kohel <kohel@maths.usyd.edu.au>
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.number_fields import NumberFields
_NumberFields = NumberFields()
from sage.rings.integer_ring import ZZ
from sage.rings.number_field.order import is_NumberFieldOrder
from sage.rings.real_mpfr import RealField
from sage.schemes.generic.morphism import (SchemeMorphism_point, SchemeMorphism, is_SchemeMorphism)
from sage.structure.sequence import Sequence

############################################################################
# Rational points on schemes, which we view as morphisms determined
# by coordinates.
############################################################################

class SchemeMorphism_point_affine(SchemeMorphism_point):
    """
    A rational point on an affine scheme.

    INPUT:

    - ``X`` -- a subscheme of an ambient affine space over a ring `R`.

    - ``v`` -- a list/tuple/iterable of coordinates in `R`.

    - ``check`` -- boolean (optional, default:``True``). Whether to
      check the input for consistency.

    EXAMPLES::

        sage: A = AffineSpace(2, QQ)
        sage: A(1, 2)
        (1, 2)
    """
    def __init__(self, X, v, check=True):
        """
        The Python constructor.

        See :class:`SchemeMorphism_point_affine` for details.

        TESTS::

            sage: from sage.schemes.affine.affine_point import SchemeMorphism_point_affine
            sage: A3.<x,y,z> = AffineSpace(QQ, 3)
            sage: SchemeMorphism_point_affine(A3(QQ), [1, 2, 3])
            (1, 2, 3)
        """
        SchemeMorphism.__init__(self, X)
        if check:
            from sage.rings.ring import CommutativeRing
            if is_SchemeMorphism(v):
                v = list(v)
            else:
                try:
                    if isinstance(v.parent(), CommutativeRing):
                        v = [v]
                except AttributeError:
                    pass
            # Verify that there are the right number of coords
            d = self.codomain().ambient_space().ngens()
            if len(v) != d:
                raise TypeError("argument v (=%s) must have %s coordinates"%(v, d))
            if not isinstance(v, (list, tuple)):
                raise TypeError("argument v (= %s) must be a scheme point, list, or tuple"%str(v))
            # Make sure the coordinates all lie in the appropriate ring
            v = Sequence(v, X.value_ring())
            # Verify that the point satisfies the equations of X.
            X.extended_codomain()._check_satisfies_equations(v)
        self._coords = tuple(v)

    def nth_iterate(self, f, n):
        r"""
        Returns the point `f^n(self)`

        INPUT:

        - ``f`` -- a :class:`SchemeMorphism_polynomial` with ``self`` if ``f.domain()``.

        - ``n`` -- a positive integer.

        OUTPUT:

        - a point in ``f.codomain()``.

        EXAMPLES::

            sage: A.<x,y> = AffineSpace(QQ, 2)
            sage: H = Hom(A, A)
            sage: f = H([(x-2*y^2)/x,3*x*y])
            sage: A(9,3).nth_iterate(f, 3)
            doctest:warning
            ...
            (-104975/13123, -9566667)
        """
        from sage.misc.superseded import deprecation
        deprecation(23479, "use f.nth_iterate(P, n) instead")
        if self.codomain() != f.domain():
            raise TypeError("point is not defined over domain of function")
        if f.domain() != f.codomain():
            raise TypeError("domain and codomain of function not equal")
        if n == 0:
            return(self)
        else:
            Q = f(self)
            for i in range(2, n+1):
                Q = f(Q)
            return(Q)

    def orbit(self, f, N):
        r"""
        Returns the orbit of the point by `f`.

        If `n` is an integer it returns `[self,f(self), \ldots, f^{n}(self)]`.

        If `n` is a list or tuple `n=[m, k]` it returns `[f^{m}(self), \ldots, f^{k}(self)]`.

        INPUT:

        - ``f`` -- a :class:`SchemeMorphism_polynomial` with the point in ``f.domain()``.

        - ``N`` -- a non-negative integer or list or tuple of two non-negative integers.

        OUTPUT:

        - a list of points in ``f.codomain()``.

        EXAMPLES::

            sage: A.<x,y>=AffineSpace(QQ, 2)
            sage: H = Hom(A, A)
            sage: f = H([(x-2*y^2)/x, 3*x*y])
            sage: A(9, 3).orbit(f, 3)
            doctest:warning
            ...
            [(9, 3), (-1, 81), (13123, -243), (-104975/13123, -9566667)]
        """
        from sage.misc.superseded import deprecation
        deprecation(23479, "use f.orbit(P, n) instead")
        Q = self
        if isinstance(N, list) or isinstance(N, tuple):
            Bounds = list(N)
        else:
            Bounds = [0,N]
        for i in range(1, Bounds[0]+1):
            Q = f(Q)
        Orb = [Q]
        for i in range(Bounds[0]+1, Bounds[1]+1):
            Q = f(Q)
            Orb.append(Q)
        return(Orb)

    def global_height(self, prec=None):
        r"""
        Returns the logarithmic height of the point.

        INPUT:

        - ``prec`` -- desired floating point precision (default:
          default RealField precision).

        OUTPUT:

        - a real number.

        EXAMPLES::

            sage: P.<x,y> = AffineSpace(QQ, 2)
            sage: Q = P(41, 1/12)
            sage: Q.global_height()
            3.71357206670431

        ::

            sage: P = AffineSpace(ZZ, 4, 'x')
            sage: Q = P(3, 17, -51, 5)
            sage: Q.global_height()
            3.93182563272433

        ::

            sage: R.<x> = PolynomialRing(QQ)
            sage: k.<w> = NumberField(x^2+5)
            sage: A = AffineSpace(k, 2, 'z')
            sage: A([3, 5*w+1]).global_height(prec=100)
            2.4181409534757389986565376694

        .. TODO::

            P-adic heights.
        """
        if self.domain().base_ring() == ZZ:
            if prec is None:
                R = RealField()
            else:
                R = RealField(prec)
            H = max([self[i].abs() for i in range(self.codomain().ambient_space().dimension_relative())])
            return(R(max(H,1)).log())
        if self.domain().base_ring() in _NumberFields or is_NumberFieldOrder(self.domain().base_ring()):
            return(max([self[i].global_height(prec) for i in range(self.codomain().ambient_space().dimension_relative())]))
        else:
            raise NotImplementedError("must be over a number field or a number field Order")

    def homogenize(self, n):
        r"""
        Return the homogenization of the point at the ``nth`` coordinate.

        INPUT:

        - ``n`` -- integer between 0 and dimension of the map, inclusive.

        OUTPUT:

        - A point in the projectivization of the codomain of the map .

        EXAMPLES::

            sage: A.<x,y> = AffineSpace(ZZ, 2)
            sage: Q = A(2, 3)
            sage: Q.homogenize(2).dehomogenize(2) == Q
            True

            ::

            sage: A.<x,y> = AffineSpace(QQ, 2)
            sage: Q = A(2, 3)
            sage: P = A(0, 1)
            sage: Q.homogenize(2).codomain() == P.homogenize(2).codomain()
            True
        """
        phi = self.codomain().projective_embedding(n)
        return(phi(self))

class SchemeMorphism_point_affine_field(SchemeMorphism_point_affine):

    def weil_restriction(self):
        r"""
        Compute the Weil restriction of this point over some extension
        field.

        If the field is a finite field, then this computes
        the Weil restriction to the prime subfield.

        A Weil restriction of scalars - denoted `Res_{L/k}` - is a
        functor which, for any finite extension of fields `L/k` and
        any algebraic variety `X` over `L`, produces another
        corresponding variety `Res_{L/k}(X)`, defined over `k`. It is
        useful for reducing questions about varieties over large
        fields to questions about more complicated varieties over
        smaller fields. This functor applied to a point gives
        the equivalent point on the Weil restriction of its
        codomain.

        OUTPUT: Scheme point on the Weil restriction of the codomain of this point.

        EXAMPLES::

            sage: A.<x,y,z> = AffineSpace(GF(5^3, 't'), 3)
            sage: X = A.subscheme([y^2-x*z, z^2+y])
            sage: Y = X.weil_restriction()
            sage: P = X([1, -1, 1])
            sage: Q = P.weil_restriction();Q
            (1, 0, 0, 4, 0, 0, 1, 0, 0)
            sage: Q.codomain() == Y
            True

        ::

            sage: R.<x> = QQ[]
            sage: K.<w> = NumberField(x^5-2)
            sage: R.<x> = K[]
            sage: L.<v> = K.extension(x^2+w)
            sage: A.<x,y> = AffineSpace(L, 2)
            sage: P = A([w^3-v,1+w+w*v])
            sage: P.weil_restriction()
            (w^3, -1, w + 1, w)
        """
        L = self.codomain().base_ring()
        WR = self.codomain().weil_restriction()
        if L.is_finite():
            d = L.degree()
            if d == 1:
                return(self)
            newP = []
            for t in self:
                c = t.polynomial().coefficients(sparse=False)
                c = c + (d-len(c))*[0]
                newP += c
        else:
            d = L.relative_degree()
            if d == 1:
                return(self)
            #create a CoordinateFunction that gets the relative coordinates in terms of powers
            from sage.rings.number_field.number_field_element import CoordinateFunction
            v = L.gen()
            V, from_V, to_V = L.relative_vector_space()
            h = L(1)
            B = [to_V(h)]
            f = v.minpoly()
            for i in range(f.degree()-1):
                h *= v
                B.append(to_V(h))
            W = V.span_of_basis(B)
            p = CoordinateFunction(v, W, to_V)
            newP = []
            for t in self:
                newP += p(t)
        return(WR(newP))

    def intersection_multiplicity(self, X):
        r"""
        Return the intersection multiplicity of the codomain of this point and ``X`` at this point.

        This uses the intersection_multiplicity implementations for projective/affine subschemes. This
        point must be a point on an affine subscheme.

        INPUT:

        - ``X`` -- a subscheme in the same ambient space as that of the codomain of this point.

        OUTPUT: Integer.

        EXAMPLES::

            sage: A.<x,y> = AffineSpace(GF(17), 2)
            sage: X = A.subscheme([y^2 - x^3 + 2*x^2 - x])
            sage: Y = A.subscheme([y - 2*x + 2])
            sage: Q1 = Y([1,0])
            sage: Q1.intersection_multiplicity(X)
            2
            sage: Q2 = X([4,6])
            sage: Q2.intersection_multiplicity(Y)
            1

        ::

            sage: A.<x,y,z,w> = AffineSpace(QQ, 4)
            sage: X = A.subscheme([x^2 - y*z^2, z - 2*w^2])
            sage: Q = A([2,1,2,-1])
            sage: Q.intersection_multiplicity(X)
            Traceback (most recent call last):
            ...
            TypeError: this point must be a point on an affine subscheme
        """
        from sage.schemes.affine.affine_space import is_AffineSpace
        if is_AffineSpace(self.codomain()):
            raise TypeError("this point must be a point on an affine subscheme")
        return self.codomain().intersection_multiplicity(X, self)

    def multiplicity(self):
        r"""
        Return the multiplicity of this point on its codomain.

        Uses the subscheme multiplicity implementation. This point must be a point on an
        affine subscheme.

        OUTPUT: an integer.

        EXAMPLES::

            sage: A.<x,y,z> = AffineSpace(QQ, 3)
            sage: X = A.subscheme([y^2 - x^7*z])
            sage: Q1 = X([1,1,1])
            sage: Q1.multiplicity()
            1
            sage: Q2 = X([0,0,2])
            sage: Q2.multiplicity()
            2
        """
        from sage.schemes.affine.affine_space import is_AffineSpace
        if is_AffineSpace(self.codomain()):
            raise TypeError("this point must be a point on an affine subscheme")
        return self.codomain().multiplicity(self)

class SchemeMorphism_point_affine_finite_field(SchemeMorphism_point_affine_field):

    def __hash__(self):
        r"""
        Returns the integer hash of the point.

        OUTPUT: Integer.

        EXAMPLES::

            sage: P.<x,y,z> = AffineSpace(GF(5), 3)
            sage: hash(P(2, 1, 2))
            57

        ::

            sage: P.<x,y,z> = AffineSpace(GF(7), 3)
            sage: X = P.subscheme(x^2-y^2)
            sage: hash(X(1, 1, 2))
            106

        ::

            sage: P.<x,y> = AffineSpace(GF(13), 2)
            sage: hash(P(3, 4))
            55

        ::

            sage: P.<x,y> = AffineSpace(GF(13^3, 't'), 2)
            sage: hash(P(3, 4))
            8791
        """
        p = self.codomain().base_ring().order()
        N = self.codomain().ambient_space().dimension_relative()
        return sum(hash(self[i])*p**i for i in range(N))

    def orbit_structure(self, f):
        r"""
        This function returns the pair `[m, n]` where `m` is the
        preperiod and `n` is the period of the point by ``f``.

        Every point is preperiodic over a finite field.


        INPUT:

        - ``f`` -- a :class:`ScemeMorphism_polynomial` with the point in ``f.domain()``.

        OUTPUT:

        - a list `[m, n]` of integers.

        EXAMPLES::

            sage: P.<x,y,z> = AffineSpace(GF(5), 3)
            sage: f = DynamicalSystem_affine([x^2 + y^2, y^2, z^2 + y*z], domain=P)
            sage: f.orbit_structure(P(1, 1, 1))
            [0, 6]

        ::

            sage: P.<x,y,z> = AffineSpace(GF(7), 3)
            sage: X = P.subscheme(x^2 - y^2)
            sage: f = DynamicalSystem_affine([x^2, y^2, z^2], domain=X)
            sage: f.orbit_structure(X(1, 1, 2))
            [0, 2]

        ::

            sage: P.<x,y> = AffineSpace(GF(13), 2)
            sage: f = DynamicalSystem_affine([x^2 - y^2, y^2], domain=P)
            sage: P(3, 4).orbit_structure(f)
            doctest:warning
            ...
            [2, 6]

        ::

            sage: P.<x,y> = AffineSpace(GF(13), 2)
            sage: H = End(P)
            sage: f = H([x^2 - y^2, y^2])
            sage: f.orbit_structure(P(3, 4))
            doctest:warning
            ...
            [2, 6]
        """
        from sage.misc.superseded import deprecation
        deprecation(23479, "use f.orbit_structure(P, n) instead")
        try:
            return f.orbit_structure(self)
        except AttrbuteError:
            raise TypeError("map must be a dynamical system")
