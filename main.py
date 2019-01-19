# A program by Yam Mandelblit Zachar

# This program reads data from an input file and checks for problems in the data. If no problem was found,
# the program plots the data and returns a graph with a linear fit and the parameters of that fit, as well
# as the values of chi2 and chi2_reduced.

from math import sqrt
from matplotlib import pyplot

# This function converts the lines from the file into a list of rows. Then it converts all the items in that list
# to be lowercased.
def file_text_to_lists(lines):
    rows = []
    i = 0
    while lines[i] != "":
        row = lines[i].split(" ")
        lower_row = []
        for element in row:
            lower_row.append(element.lower())
        rows.append(lower_row)

        i = i + 1
    return rows

# This function terminates the program when an error was identified.
def throw_error(message):
    print(message)
    raise SystemExit(0)

# This function converts the "rows" in the rows list into a dictionary, in which the key of each item
# is the type of the variable(x,y,dx,dy), and the values are the values of each of those variables.
def lists_to_dict(data):
    end_data = {}
    for row in data:
        title = row[0]
        end_data[title] = row[1:]
        for i in range(len(end_data[title])):
            end_data[title][i] = float(end_data[title][i])

    return end_data

# This function reads the lines and identifies the title and unit measurements of each axis.
def read_legends(end_data, lines):
    for line in lines:
        if "axis" in line:
            parts = line.split(": ")
            end_data[parts[0]] = parts[1]

        if line.startswith("a") or line.startswith("b"):
            end_data[line[0]] = line.split(" ")[1:]
            for i in range(len(end_data[line[0]])):
                end_data[line[0]][i] = float(end_data[line[0]][i])

    return end_data

# This function opens the input file, reads it and converts it into a dictionary with all the variables
# and their values.
def read_file(filename):
    file = open(filename, "r")
    lines = file.read().splitlines()
    file.close()

    rows = file_text_to_lists(lines)

    # Here, the function checks whether the data is written in rows or in columns, and if any problem was found
    # it calls the "throw_error" function and print an error message.
    is_columns = "x" not in rows[1] and "y" not in rows[1] and "dx" not in rows[1] and "dy" not in rows[1]
    if is_columns:
        data = [[], [], [], []]
        for row in rows:
            if len(row) == 4 and "" not in row:
                for i in range(0, 4):
                    data[i].append(row[i])

            else:
                throw_error("Input file error: Data lists are not the same length.")
    else:
        if len(rows) == 4:
            for row in rows:
                if len(row) != len(rows[0]) and "" not in row:
                    throw_error("Input file error: Data lists are not the same length.")

            data = rows
        else:
            throw_error("Input file error: Data lists are not the same length.")

    for row in data:
        if row[0].startswith("d"):
            for i in row[1:]:
                if float(i) <= 0:
                    throw_error("Input file error: Not all uncertainties are positive.")

    end_data = lists_to_dict(data)
    end_data = read_legends(end_data, lines)

    return end_data


# This function is used to calculate the average of each variable needed for the fit as it was
# written in the project instructions.
def avg(lst, dy_squared):
    sum_top = 0
    sum_bottom = 0
    for i in range(len(lst)):
        sum_top += lst[i] / dy_squared[i]
        sum_bottom += 1 / dy_squared[i]
    return sum_top / sum_bottom

# This function prints the output of the variables for the linear fit and the value of chi2 and chi2_reduced.
def write_output(a, b, da, db, chi, chi_reduced):
    print("a =", a, "+-", da)
    print("b =", b, "+-", db)
    print("chi2 =", chi)
    print("chi2_reduced =", chi_reduced)

# This function plots the data according to the instructions that were given.
def plot(data, a, b):
    pyplot.plot([min(data["x"]), max(data["x"])], [a * min(data["x"]) + b, a * max(data["x"]) + b], color="red")
    pyplot.errorbar(data["x"], data["y"], xerr=data["dx"], yerr=data["dy"], linestyle="None", color="blue")
    pyplot.xlabel(data["x axis"])
    pyplot.ylabel(data["y axis"])
    pyplot.savefig("linear_fit.svg")
    # pyplot.show()

# This function is the main function of the program. It computes the variables for the linear fit
# and use the "plot" function to create a graph of the data points and the linear fit according to
# the instructions.
def fit_linear(filename):
    data = read_file(filename)
    n = len(data["x"])
    xy = []
    x_squared = []
    dy_squared = []
    for i in range(n):
        xy.append(data["x"][i] * data["y"][i])
        x_squared.append(data["x"][i] ** 2)
        dy_squared.append(data["dy"][i] ** 2)

    a = (avg(xy, dy_squared) - avg(data["x"], dy_squared) * avg(data["y"], dy_squared)) / (avg(x_squared, dy_squared) - avg(data["x"], dy_squared) ** 2)
    b = avg(data["y"], dy_squared) - a * avg(data["x"], dy_squared)
    da = sqrt(avg(dy_squared, dy_squared) / (n * (avg(x_squared, dy_squared) - avg(data["x"], dy_squared) ** 2)))
    db = sqrt(avg(dy_squared, dy_squared) * avg(x_squared, dy_squared) / (n * (avg(x_squared, dy_squared) - avg(data["x"], dy_squared) ** 2)))

    chi = 0
    for i in range(n):
        chi = chi + ((data["y"][i] - a * data["x"][i] - b) / data["dy"][i]) ** 2

    chi_reduced = chi / (n - 2)
    write_output(a, b, da, db, chi, chi_reduced)
    plot(data, a, b)



