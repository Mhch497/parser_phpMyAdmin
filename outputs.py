from prettytable import PrettyTable


def default_output(results):
    for row in results[1:]:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)
