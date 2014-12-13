def cplot3d(expr, xlim = [-1, 1], ylim = [-1, 1], points = 50, type = "real-imag", style = "color"):
    """
    Plot complex expressions or functions.
    
       expr      - expression or function to plot.
       xlim      - max and min 'x' values, default [-1, 1].
       ylim      - max and min 'y' values, default [-1, 1].
       points    - axis points. Total points**2.
       type      - type of plot, default "real-imag".
                   Opctions: "mod-arg" "real-arg" "arg-real" "real-imag"
       style     - "color": color plot.
                   others: double plot.
    """

    # Dependences
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    import matplotlib.pyplot as plt
    from numpy import arange, array, meshgrid, size, absolute, angle
    from sympy import lambdify, Symbol
    
    # Expressions to functions
    if hasattr(expr, 'atoms'):
        var = list(expr.atoms(Symbol))[0]
        Fz=lambdify(var, expr, 'numpy')
    else:
        Fz=expr

    # Obtain X(real), Y(real), Z(imaginary)
    X = arange(xlim[0], xlim[1], (xlim[1]-xlim[0])/(points-1))
    Y = arange(ylim[0], ylim[1], (ylim[1]-ylim[0])/(points-1))
    X, Y = meshgrid(X, Y)
    R=Fz(X + 1j*Y)

    # Select type
    if type == "mod-arg":
        Z = absolute(R)
        T = angle(R)
        zlabel = "abs(f(z))"
        keyhue = "arg(f(z))"
    elif type == "real-arg":
        Z = R.real
        T = angle(R)
        zlabel = "Re(f(z))"
        keyhue = "arg(f(z))"
    elif type == "arg-real":
        Z = angle(R)
        T = R.real
        zlabel = "arg(f(z))"
        keyhue = "Re(f(z))"
    elif type == "real-imag":
        Z = R.real
        T = R.imag
        zlabel = "Re(f(z))"
        keyhue = "Im(f(z))"


    # Select style
    if style == "color":
        #  Normalize. hue in [0, 1]
        N = (T - T.min())/(T.max() - T.min())

        # Setup the plot
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

        # Show the leyend
        m = cm.ScalarMappable(cmap=cm.jet, norm=surf.norm)
        m.set_array(T)
        p=plt.colorbar(m)
        p.set_label('$\mathrm{'+keyhue+'}$')
    else:
        # Setup first plot
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
        # Setup second plot
        ax = fig.add_subplot(1, 2, 2, projection='3d')
        ax.set_xlabel('$\mathrm{Re(z)}$')
        ax.set_ylabel('$\mathrm{Im(z)}$')
        ax.set_zlabel('$\mathrm{'+keyhue+'}$')
        surf = ax.plot_surface(
            X, Y, T, rstride=1, cstride=1,
            cmap=cm.jet,
            linewidth=0, antialiased=False, shade=False)
