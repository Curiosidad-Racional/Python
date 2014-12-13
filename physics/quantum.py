# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 19:56:31 2013

@author: edo
"""

from sympy import Add, Mul, Pow, S, E, I, sin, cos, exp

from sympy.core.trace import Tr
from sympy.physics.quantum.anticommutator import AntiCommutator
from sympy.physics.quantum.commutator import Commutator
from sympy.physics.quantum.density import Density, entropy, fidelity
from sympy.physics.quantum.state import Ket, Bra, TimeDepKet, State, KetBase, BraBase, Wavefunction
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.gate import HadamardGate
from sympy.physics.quantum.represent import represent
from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.cartesian import XKet, PxKet, PxOp, XOp
from sympy.physics.quantum.spin import JzKet, Jz
from sympy.physics.quantum.innerproduct import InnerProduct
from sympy.physics.quantum.operator import OuterProduct, Operator, HermitianOperator, UnitaryOperator, DifferentialOperator
from sympy.physics.quantum.operatorset import operators_to_state
from sympy.physics.quantum.tensorproduct import TensorProduct





class Infix:
    """
    Definition of an Infix operator.

    Examples
    ========

    >>> x = Infix(lambda x,y: x*y)
    >>> 3 |x| 5
    15
    """
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

# Tensor product infix operator for quantum bites
ox = Infix(TensorProduct)


class IdempotentOperator(Operator):
    """
    Idempotent operator class.

    Examples
    ========

    >>> from sympy import *
    >>> A = symbols('A', cls=IdempotentOperator)
    >>> A**2
    A
    >>> A**100
    A
    """
    is_idempotent = True
    def _eval_inverse(self):
        raise ZeroDivisionError('Idempotent matrix has no inverse.')

    def _eval_power(self, exp):
        if exp < 0:
            raise ZeroDivisionError('Idempotent matrix has no inverse.')
        elif exp == 0:
            return 1
        else:
            return self
        return self


def Qperm(n, f, *param):
    dim = 2**n
    _Qperm_ = 0
    param = [""] + list(param)
    for k in range(dim):
        bits = ("%0" + str(n) + "d") % int(bin(k)[2:])
        param[0] = bits        
        pbits = f(*param)
        _Qperm_ += OuterProduct(Qubit(bits), Qubit(pbits).dual)
    return _Qperm_


def shift(subject, direction = 1):
    """
    Shift 'subject'. 'direction' = 1 right shift, 'direction' = -1 left shift.
    """
    if direction == 1:
        tmp = subject[-1]
        subject = tmp + subject[:-1]
    elif direction == -1:
        tmp = subject[0]
        subject = subject[1:] + tmp
    return subject


def inter(subject, indexes, direction = 1):
    """
    Shift only 'indexes' positions.
    """
    indexes.sort()
    while (indexes[0] < 0):
        indexes.append(indexes[0])
        del indexes[0]
    selection = ""
    for i in indexes:
        selection += subject[i]
    selection = shift(selection, direction)
    result = subject[:indexes[0]]
    for i in range(len(indexes)-1):
        result += selection[i] + subject[indexes[i] + 1:indexes[i+1]]
    result += selection[-1]
    if indexes[-1] != -1:
        result += subject[indexes[-1] + 1:]
    return result


def Qident(n):
    """
    Quantum identity operator over 'n' qubits.
    """
    dim = 2**n
    result = 0
    for i in range(dim):
        bits = ("%0" + str(n) + "d") % int(bin(i)[2:])
        result += OuterProduct(Qubit(bits), Qubit(bits).dual)
    return result


def Psym(n):
    """
    Quantum symmetric operator over 'n' qubits.
    """
    dim = 2**n
    result = 0
    for i in range(dim):
        ibits = ("%0" + str(n) + "d") % int(bin(i)[2:])
        result += OuterProduct(Qubit(ibits*2), Qubit(ibits*2).dual)
        for j in range(i):
            jbits = ("%0" + str(n) + "d") % int(bin(j)[2:])
            result += OuterProduct(Qubit(ibits+jbits), Qubit(ibits+jbits).dual)/2
            result += OuterProduct(Qubit(jbits+ibits), Qubit(jbits+ibits).dual)/2
            result += OuterProduct(Qubit(ibits+jbits), Qubit(jbits+ibits).dual)/2
            result += OuterProduct(Qubit(jbits+ibits), Qubit(ibits+jbits).dual)/2
    return result


def BlochState(theta, phi):
    """
    Quantum bit Bloch representation.
    """
    _BlochState_ = cos(theta/2)*exp(I*phi/2)*Qubit('0') + sin(theta/2)*exp(-I*phi/2)*Qubit('1')
    return _BlochState_



def Outer2Mul(e, **options):
    """
    Expand quantum sympy simplification.
    """
    if e == 0:
        return S.Zero

    # If we just have a raw ket, return it.
    if isinstance(e, KetBase):
        return e

    # We have an Add(a, b, c, ...) and compute
    # Add(qapply(a), qapply(b), ...)
    elif isinstance(e, Add):
        result = 0
        for arg in e.args:
            result += Outer2Mul(arg, **options)
        return result

    # For a Density operator call qapply on its state
    elif isinstance(e, Density):
        new_args = [(Outer2Mul(state, **options),prob) for (state,prob) in e.args]
        return Density(*new_args)

    # For a raw TensorProduct, call qapply on its args.
    elif isinstance(e, TensorProduct):
        return TensorProduct(*[Outer2Mul(t, **options) for t in e.args])

    # For a Pow, call qapply on its base.
    elif isinstance(e, Pow):
        return Outer2Mul(e.base, **options)**e.exp

    # We have a Mul where there might be actual operators to apply to kets.
    elif isinstance(e, Mul):
        result = 1
        for arg in e.args:
            result *= Outer2Mul(arg, **options)
        return result

    # Change OuterProduct for Mul
    elif isinstance(e, OuterProduct):
        result = Mul(e.ket, e.bra)
        return result        

    # In all other cases (State, Operator, Pow, Commutator, InnerProduct,
    # OuterProduct) we won't ever have operators to apply to kets.
    else:
        return e




def Mul2Outer(e, **options):
    """
    Expand quantum sympy simplification.
    """
    if e == 0:
        return S.Zero

    # If we just have a raw ket, return it.
    if isinstance(e, KetBase):
        return e

    # We have an Add(a, b, c, ...) and compute
    # Add(qapply(a), qapply(b), ...)
    elif isinstance(e, Add):
        result = 0
        for arg in e.args:
            result += Mul2Outer(arg, **options)
        return result

    # For a Density operator call qapply on its state
    elif isinstance(e, Density):
        new_args = [(Mul2Outer(state, **options),prob) for (state,prob) in e.args]
        return Density(*new_args)

    # For a raw TensorProduct, call qapply on its args.
    elif isinstance(e, TensorProduct):
        return TensorProduct(*[Mul2Outer(t, **options) for t in e.args])

    # For a Pow, call qapply on its base.
    elif isinstance(e, Pow):
        return Mul2Outer(e.base, **options)**e.exp

    # Change Mul for OuterProduct
    elif isinstance(e, Mul):
        result = 1
        indexes = []
        args = list(e.args)
        for i in range(len(args)-1):
            if isinstance(args[i], KetBase) and isinstance(args[i+1], BraBase):
                args[i] = OuterProduct(args[i], args[i+1])
                indexes.append(i+1)
        for i in indexes:
            del args[i]
        for arg in args:
            result *= Mul2Outer(arg, **options)
        return result

    # Process the trace.
    elif isinstance(e, Tr):
        new_args = Mul2Outer(e.args[0], **options)
        return Tr(new_args, e.args[1])

    # In all other cases (State, Operator, Pow, Commutator, InnerProduct,
    # OuterProduct) we won't ever have operators to apply to kets.
    else:
        return e




#####################################
## Qperm test code
#
#####################################
## Idempotent test code
#
#Idem = IdempotentOperator('Idem')
#print Idem**2
#print Idem**3
#print Idem**4
##print Idem**-1
#print Idem**0
#####################################
## Mul2Outer test code
#
#tmp0 = Mul(Qubit('0'),Qubit('1').dual)
#tmp1 = Mul2Outer(tmp0)
#tmp2 = Tr(tmp0).doit()
#tmp3 = Tr(tmp1).doit()
#tmp4 = Mul2Outer(tmp2).doit()
#tmp5 = ""
#tmp0 = Outer2Mul(Psym(2))
#tmp1 = Tr(tmp0)
#tmp2 = tmp1.doit()
#tmp3 = Mul2Outer(tmp2)
#tmp4 = tmp3.doit()
#tmp5 = qapply(tmp4)
#print tmp0
#print "-----------------------"
#print tmp1
#print "-----------------------"
#print tmp2
#print "-----------------------"
#print tmp3
#print "-----------------------"
#print tmp4
#print "-----------------------"
#print tmp5
#####################################
## Outer2Mul test code
#
#tmp0 = Psym(2)
#tmp1 = Outer2Mul(tmp0)
#tmp2 = tmp1**2
#tmp3 = qapply(tmp2-tmp1)
#tmp4 = Outer2Mul(tmp3)
#tmp5 = qapply(tmp4)
#print tmp0
#print "-----------------------"
#print tmp1
#print "-----------------------"
#print tmp2
#print "-----------------------"
#print tmp3
#print "-----------------------"
#print tmp4
#print "-----------------------"
#print tmp5
#####################################
## Psym test code
#
#print Psym(1)
#print "-----------------------"
#print Psym(2)
#print "-----------------------"
#print qapply(Psym(1)**2 - Psym(1))
#print "-----------------------"
#print represent(Psym(1))
#####################################
## BlochState test code
#
#from sympy import symbols, simplify
#x, y = symbols('x y', real=True)
#a = BlochState(x,y)
#print qapply(Dagger(a)*a)
#print simplify(qapply(Dagger(a)*a))
