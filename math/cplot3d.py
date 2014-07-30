def cplot3d(expr, xlim = [-1, 1], ylim = [-1, 1], points = 50, style = "real-imag"):
    # Importaciones necesarias
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    import matplotlib.pyplot as plt
    from numpy import arange, array, meshgrid, abs, size, absolute, angle
    from sympy import Symbol, lambdify

    # Para poder representar tanto funciones como expresiones
    # transformamos las expresiones en funciones.
    if hasattr(expr, 'atoms'):
        var = list(expr.atoms(Symbol))[0]
        Fz=lambdify(var, expr, 'numpy')
    else:
        Fz=expr

    # Obtenemos los valores de X, Y, Z
    X = arange(xlim[0], xlim[1], (xlim[1]-xlim[0])/(points-1))
    Y = arange(ylim[0], ylim[1], (ylim[1]-ylim[0])/(points-1))
    X, Y = meshgrid(X, Y)
    R=Fz(X + 1j*Y)
    if style == "abs-angle":
        Z = absolute(R)
        T = angle(R)
        zlabel = "abs(f(z))"
        keyhue = "arg(f(z))"
    elif style == "real-angle":
        Z = R.real
        T = angle(R)
        zlabel = "Re(f(z))"
        keyhue = "arg(f(z))"
    elif style == "angle-real":
        Z = angle(R)
        T = R.real
        zlabel = "arg(f(z))"
        keyhue = "Re(f(z))"
    elif style == "real-imag":
        Z = R.real
        T = R.imag
        zlabel = "Re(f(z))"
        keyhue = "Im(f(z))"
    # Normaliza dado que hue toma valores de 0 a 1
    N = (T - T.min())/(T.max() - T.min())

    # Preparamos el plot
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    plt.title('$\mathrm{f(z)}$')
    ax.set_xlabel('$\mathrm{Re(z)}$')
    ax.set_ylabel('$\mathrm{Im(z)}$')
    ax.set_zlabel('$\mathrm{'+zlabel+'}$')
    surf = ax.plot_surface(
        X, Y, Z, rstride=1, cstride=1,
        facecolors=cm.jet(N),
        linewidth=0, antialiased=True, shade=False)

    # Mostramos la leyenda
    m = cm.ScalarMappable(cmap=cm.jet, norm=surf.norm)
    m.set_array(T)
    p=plt.colorbar(m)
    p.set_label('$\mathrm{'+keyhue+'}$')
