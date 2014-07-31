def cplot3d(expr, xlim = [-1, 1], ylim = [-1, 1], points = 50, variables = "real-imag", style = "color"):
    """
    Representa expresiones o funciones complejas.
    
       expr      - expresión o función a representar.
       xlim      - valores máximo y mínimo de la 'x', por defecto [-1, 1].
       ylim      - valores máximo y mínimo de la 'y', por defecto [-1, 1].
       points    - puntos usados para representar por cada dimensión: en
                   total points**2 puntos.
       variables - texto que indica las variables que se representarán,
                      por defecto "real-imag".
                   Opciones: "mod-arg" "real-arg" "arg-real" "real-imag"
       style     - texto que indica el tipo de representación:
                   "color": un sólo gráfico en el que la segunda variable
                      es el color.
                   "" u otros: dos gráficos, el primero para la parte real
                      de la función, el segundo para la parte imaginaria.
    """

    # Importaciones necesarias
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    import matplotlib.pyplot as plt
    from numpy import arange, array, meshgrid, size, absolute, angle
    from sympy import lambdify, Symbol
    
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

    # Elegimos variables a representar
    if variables == "mod-arg":
        Z = absolute(R)
        T = angle(R)
        zlabel = "abs(f(z))"
        keyhue = "arg(f(z))"
    elif variables == "real-arg":
        Z = R.real
        T = angle(R)
        zlabel = "Re(f(z))"
        keyhue = "arg(f(z))"
    elif variables == "arg-real":
        Z = angle(R)
        T = R.real
        zlabel = "arg(f(z))"
        keyhue = "Re(f(z))"
    elif variables == "real-imag":
        Z = R.real
        T = R.imag
        zlabel = "Re(f(z))"
        keyhue = "Im(f(z))"


    # Elegimos el tipo de representación
    if style == "color":
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
    else:
        # Preparamos el primer plot
        fig = plt.figure(figsize=plt.figaspect(0.5))
        plt.axis('off')
        plt.title('$\mathrm{f(z)}$')
        ax = fig.add_subplot(1, 2, 1, projection='3d')
        ax.set_xlabel('$\mathrm{Re(z)}$')
        ax.set_ylabel('$\mathrm{Im(z)}$')
        ax.set_zlabel('$\mathrm{'+zlabel+'}$')
        surf = ax.plot_surface(
            X, Y, Z, rstride=1, cstride=1,
            cmap=cm.jet,
            linewidth=0, antialiased=False, shade=False)
        # Preparamos el segundo plot
        ax = fig.add_subplot(1, 2, 2, projection='3d')
        ax.set_xlabel('$\mathrm{Re(z)}$')
        ax.set_ylabel('$\mathrm{Im(z)}$')
        ax.set_zlabel('$\mathrm{'+keyhue+'}$')
        surf = ax.plot_surface(
            X, Y, T, rstride=1, cstride=1,
            cmap=cm.jet,
            linewidth=0, antialiased=False, shade=False)
