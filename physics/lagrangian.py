from sympy import Symbol, simplify, Derivative, Function, diff, Equality, Matrix, gcd, cancel, integrate, Integral
def syst2matrix(system, variables=None):
    """
    Returns A, B matrices of the system A·X = B.

    Examples
    ========

    >>> from sympy import *
    >>> x, y, z = symbols('x y z')
    >>> syst = [ 2*x + 3*y - 10, - 3*x + 5*y - 7 ]
    >>> syst2matrix(syst)
    ⎛⎡2   3⎤, ⎡10⎤⎞
    ⎜⎢     ⎥  ⎢  ⎥⎟
    ⎝⎣-3  5⎦  ⎣7 ⎦⎠

    >>> syst = [ Eq(2*x + 3*y, 10), Eq(- 3*x + 5*y, 7) ]
    >>> syst2matrix(syst)
    ⎛⎡3  2 ⎤, ⎡10⎤⎞
    ⎜⎢     ⎥  ⎢  ⎥⎟
    ⎝⎣5  -3⎦  ⎣7 ⎦⎠

    >>> syst = [ Eq(2*x + 3*y, 10), - 3*x + 5*y - 7 ]
    >>> syst2matrix(syst)
    ⎛⎡3  2 ⎤, ⎡10⎤⎞
    ⎜⎢     ⎥  ⎢  ⎥⎟
    ⎝⎣5  -3⎦  ⎣7 ⎦⎠
    """
    if variables == None:
        variables = []
        for equation in system:
            variables += list(equation.atoms(Symbol))
        variables = list(set(variables))
    else:
        variables = list(set(variables))
    vars_to_zero = { k: 0 for k in variables }
    matrix_of_the_system = []
    const_of_the_system = []
    for equation in system:
        matrix_of_the_system.append([])
        if isinstance(equation, Equality):
            equation = (equation.lhs - equation.rhs)
        const_of_the_system.append(-equation.subs(vars_to_zero))
        for variable in variables:
            matrix_of_the_system[-1].append(equation.expand().collect(variable).coeff(variable))
    return Matrix(matrix_of_the_system), Matrix(const_of_the_system)

def factordet(Mat):
    """
    Extract common factors of the determinant of the matrix.

    Examples
    ========

    >>> from sympy import *
    >>> x, y, z = symbols('x y z')
    >>> A = Matrix([[x,x*y],[y*z,z]])
    >>> factordet(A)
    x*z
    """
    fact = 1
    ncols = Mat.cols
    for i in range(ncols):
        col = Mat.col(i)
        common = gcd(list(col))
        if (common != 0)&(common != 1):
            fact *= common
            Mat[i] = Matrix(list(map(cancel, col/common)))
    for j in range(Mat.rows):
        row = Mat.row(j)
        common = gcd(list(row))
        if (common != 0)&(common != 1):
            fact *= common
            Mat[j*ncols] = Matrix([list(map(cancel, row/common))])
    return fact

def solveswc(ecu_list, res_list):
    """
    Solves simplifying big linear systems.
    """
    A, B = syst2matrix(ecu_list, res_list)
    Den = Matrix(A)
    den = simplify(factordet(Den))
    Num, num = [], []
    for i in range(A.cols):
        Num.append(Matrix(A))
        Num[i][i] = B
        num.append(factordet(Num[i]))
    Den = Den.det_bareis()
    return {res_list[i]: cancel(num[i]/den)*Num[i].det_bareis()/Den for i in range(len(res_list))}

def eleq(Lagrangian, Friction = 0, t = Symbol('t')):
    """
    Returns Euler-Lagrange equations of the lagrangian system.

    Examples
    ========

    >>> from sympy import *
    >>> t, k = symbols('t k')
    >>> x = symbols('x', cls=Function)
    >>> eleq(diff(x(t),t)**2/2 - k*x(t)**2/2)
    {a_x: -k*x}

    >>> a = symbols('a')
    >>> eleq(diff(x(t),t)**2/2 - k*x(t)**2/2, a*diff(x(t),t)**2/2)
    {a_x: -*a*v_x - k*x}
    """
    Lagrangian = simplify(Lagrangian)
    var_list = [list(x.atoms(Function))[0] for x in Lagrangian.atoms(Derivative)]
    nvar = len(var_list)
    ecu_list = [ diff(Lagrangian, variable) - diff(Lagrangian, diff(variable,t), t) -  diff(Friction, diff(variable,t)) for variable in var_list ]
    str_list = [ str(variable).replace("("+str(t)+")","") for variable in var_list ]
    a_subs = {diff(var_list[i],t,2): Symbol('a_' + str_list[i]) for i in range(nvar)}
    v_subs = {diff(var_list[i],t): Symbol('v_' + str_list[i]) for i in range(nvar)}
    x_subs = {var_list[i]: Symbol(str_list[i]) for i in range(nvar)}
    for i in range(nvar):
        if hasattr(ecu_list[i], "subs"):
            ecu_list[i] = ecu_list[i].subs(a_subs).subs(v_subs).subs(x_subs)
    a_list = sorted(list(a_subs.values()), key = str)
    return solveswc(ecu_list, a_list)


def ieleq(Lagrangian, Friction = 0, t = Symbol('t')):
    """
    Returns Euler-Lagrange equations of the lagrangian system
    with first integrals.

    Examples
    ========

    >>> from sympy import *
    >>> t, k = symbols('t k')
    >>> x = symbols('x', cls=Function)
    >>> ieleq(diff(x(t),t)**2/2)
    {v_x: v_x0}

    >>> a = symbols('a')
    >>> ieleq(diff(x(t),t)**2/2, a*diff(x(t),t)**2/2)
    {v_x: -a*x + a*x0 + v_x0}
    """
    Lagrangian = simplify(Lagrangian)
    var_list = [list(x.atoms(Function))[0] for x in Lagrangian.atoms(Derivative)]
    nvar = len(var_list)
    # new variables.
    str_list = [ str(variable).replace("("+str(t)+")","") for variable in var_list ]
    a_list = [ Symbol('a_' + str_list[i]) for i in range(nvar) ]
    v_list = [ Symbol('v_' + str_list[i]) for i in range(nvar) ]
    a_subs = {diff(var_list[i],t,2): a_list[i] for i in range(nvar)}
    v_subs = {diff(var_list[i],t): v_list[i] for i in range(nvar)}
    x_subs = {var_list[i]: Symbol(str_list[i]) for i in range(nvar)}
    v0_subs = {diff(var_list[i],t): Symbol('v_' + str_list[i] + "0") for i in range(nvar)}
    x0_subs = {var_list[i]: Symbol(str_list[i] + "0") for i in range(nvar)}
    # Obtención de las ecuaciones con integrales primeras.
    a_ecu = []
    v_ecu = []
    a_var = []
    v_var = []
    for i, variable in enumerate(var_list):
        dLx = diff(Lagrangian, variable)
        dLv = diff(Lagrangian, diff(variable,t))
        dFv = diff(Friction, diff(variable,t))
        IdFv = integrate(dFv,t)
        if (dLx == 0)&(not isinstance(IdFv, Integral)):
            v_var.append(v_list[i])
            v_ecu.append(dLv.subs(v_subs).subs(x_subs) - dLv.subs(v0_subs).subs(x0_subs))
            v_ecu[-1] += IdFv.subs(v_subs).subs(x_subs) - IdFv.subs(v0_subs).subs(x0_subs)
        else:
            a_var.append(a_list[i])
            a_ecu.append((diff(dLv, t) - dLx).subs(a_subs).subs(v_subs).subs(x_subs))
            a_ecu[-1] += dFv.subs(a_subs).subs(v_subs).subs(x_subs)
    # Resolución del sistema de ecuaciones.
    sol_dict = {}
    if len(v_var) != 0:
        sol_dict.update(solveswc(v_ecu, v_var))
    if len(a_var) != 0:
        sol_dict.update(solveswc(a_ecu, a_var))
    return sol_dict

def hamiltonian(Lagrangian, t = Symbol('t'), delta = False):
    """
    Returns the Hamiltonian of the Lagrangian.

    Examples
    ========

    >>> from sympy import *
    >>> t, k = symbols('t k')
    >>> x = symbols('x', cls=Function)
    >>> hamiltonian(diff(x(t),t)**2/2 - k*x(t)**2/2)
    k*x**2/2 + v_x**2/2
    """
    Lagrangian = simplify(Lagrangian)
    var_list = [list(x.atoms(Function))[0] for x in Lagrangian.atoms(Derivative)]
    nvar = len(var_list)
    # New variables.
    str_list = [ str(variable).replace("("+str(t)+")","") for variable in var_list ]
    v_subs = {diff(var_list[i],t): Symbol('v_' + str_list[i]) for i in range(nvar)}
    x_subs = {var_list[i]: Symbol(str_list[i]) for i in range(nvar)}
    # Hamiltonian calculus.
    dxdLv = 0
    for variable in var_list:
        dxdLv += diff(variable,t)*diff(Lagrangian, diff(variable,t))
    result = simplify((dxdLv - Lagrangian).subs(v_subs).subs(x_subs))
    if delta:
        v0_subs = {Symbol('v_' + str_list[i]): Symbol('v_' + str_list[i] + "0") for i in range(nvar)}
        x0_subs = {Symbol(str_list[i]): Symbol(str_list[i] + "0") for i in range(nvar)}
        return result - result.subs(v0_subs).subs(x0_subs)
    else:
        return result
