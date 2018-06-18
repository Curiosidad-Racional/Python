try:
    import xlrd
except ImportError:
    import pip
    try:
        pip.main(["install", "xlrd"])
        import xlrd
    except AttributeError:
        from pip import _internal
        _internal.main(["install", "xlrd"])
        import xlrd

from filldict import cell, fill


book = xlrd.open_workbook("data.xlsx")
sheet = book.sheet_by_name("Limits")

def g(x, y):
    return sheet.cell_value(rowx=y, colx=x)

template = {
    cell(["a3", ..., "a5"], g, func=lambda x: x + "a"): cell((6, 0), g, rel=True, func=str)
}


print(fill(template))