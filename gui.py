from tkinter.ttk import Combobox

import os
from tkinter import *
from tkinter import font, filedialog
from tkinter import messagebox
from tkinter import ttk
import Database

import matplotlib.pyplot as plt

from QueryBuilder import QueryBuilder


def show_table(headers, widths, generator):
    """ Shows a window with listbox """
    window = Toplevel()

    row_str = ''
    for header, width in zip(headers, widths):
        row_str += ('{:<' + str(width) + '}').format(header)
    print(row_str)

    header_label = Label(window, text=row_str)
    header_label.pack(side=TOP, fill=X)

    # list box
    scrollbar = Scrollbar(window)
    scrollbar.pack(side=RIGHT, fill=Y)
    my_list = Listbox(window, yscrollcommand=scrollbar.set, bd=1)
    my_list.pack(side=TOP, fill=BOTH, expand=True)
    scrollbar.config(command=my_list.yview)

    for row in generator:
        row_str = ''
        for item, width in zip(row, widths):
            row_str += ('{:<' + str(width) + '}').format(item)
        my_list.insert(END, row_str)


def show_import_form(filename):
    """ Displays first step of creator showing first few lines of file """

    window = Toplevel()
    success = False

    top_frame = Frame(window)
    top_frame.pack(side=TOP, fill=X)

    # list box
    scrollbar = Scrollbar(top_frame, orient='horizontal')
    scrollbar.pack(side=BOTTOM, fill=X)
    my_list = Listbox(top_frame, xscrollcommand=scrollbar.set, bd=1)
    my_list.pack(side=TOP, fill=BOTH, expand=True)
    scrollbar.config(command=my_list.xview)

    # fill list box
    for row in Database.load_preview_of_file(filename, 10):
        my_list.insert(END, row)

    middle_frame = Frame(window)
    middle_frame.pack(side=TOP)

    is_header_var = IntVar(value=1)
    is_header_checkbox = Checkbutton(middle_frame, text="Does the first line include headers?", variable=is_header_var)
    is_header_checkbox.pack(side=TOP)

    delimiter_label = Label(middle_frame, text='Enter delimiter')
    delimiter_label.pack(side=TOP)

    delimiter_var = StringVar(value='\t')
    delimiter_entry = Entry(middle_frame, textvariable=delimiter_var)
    delimiter_entry.pack(side=TOP)

    def next_button_clicked():
        nonlocal success
        success = True
        window.destroy()

    next_button = Button(middle_frame, text='Next step', command=next_button_clicked)
    next_button.pack(side=TOP)

    # stops other forms from showing before user exits this window
    window.wait_window()
    return is_header_var.get(), delimiter_var.get(), success


def show_types_form(filename, headers, is_header, delimiter):
    """ Next step of database creator, this time user specifies types of columns """

    window = Toplevel()
    success = False

    top_frame = Frame(window)
    top_frame.pack(side=TOP, fill=X)

    # list box
    scrollbar = Scrollbar(top_frame, orient='horizontal')
    scrollbar.pack(side=BOTTOM, fill=X)
    my_list = Listbox(top_frame, xscrollcommand=scrollbar.set, bd=1)
    my_list.pack(side=TOP, fill=BOTH, expand=True)
    scrollbar.config(command=my_list.xview)

    for row in Database.load_preview_of_file(filename, 10):
        sep = row.split(delimiter)
        row_str = ''
        for item in sep:
            row_str += '{:<20}'.format(item)
        my_list.insert(END, row_str)

    middle_frame = Frame(window)
    middle_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH, expand=True)

    headers = headers.split(delimiter)
    headers = [''.join(c for c in header if c not in " -=[]{};',./") for header in headers]
    if not is_header:  # generates names of columns itself
        for i in range(len(headers)):
            headers[i] = 'X' + str(i+1)

    type_comboboxes = []
    fill_comboboxes = []

    for i in range(3):
        Grid.columnconfigure(middle_frame, i, weight=1)

    Label(middle_frame, text='Column name').grid(row=0, column=0, pady=5, sticky=N + S + E + W)
    Label(middle_frame, text='Type').grid(row=0, column=1, pady=5, sticky=N + S + E + W)

    for i in range(1, len(headers)+1):
        Grid.rowconfigure(middle_frame, i-1, weight=1)
        Label(middle_frame, text=headers[i-1], anchor='w').grid(row=i, column=0, pady=5, sticky=N+S+E+W)

        type_var = StringVar(value='text')
        new_widget = Combobox(middle_frame, textvariable=type_var, state="readonly", values=['text', 'integer', 'real'])
        new_widget.grid(row=i, column=1, pady=5, padx=5, sticky=N+S+E+W)
        new_widget.current(0)
        type_comboboxes.append(type_var)

    def next_button_clicked():
        nonlocal success
        success = True
        window.destroy()

    finish_button = Button(middle_frame, text="Finish importing", command=next_button_clicked)
    finish_button.grid(row=len(headers)+1, column=0, columnspan=2, pady=5)

    window.wait_window()

    types = []

    for type in type_comboboxes:
        types.append(type.get())

    return types, success


class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master = master

        # setup database
        self.database = Database.Database("data")

        # menu
        my_menu = Menu(self.master)
        self.master.config(menu=my_menu)

        my_menu.add_command(label="Exit", command=self.exitProgram)
        fileMenu = Menu(my_menu, tearoff=0)
        fileMenu.add_command(label="CSV", command=lambda: self.load_from_text('csv'))
        fileMenu.add_command(label="TXT", command=lambda: self.load_from_text('txt'))
        my_menu.add_cascade(label="Load from...", menu=fileMenu)
        my_menu.add_command(label="Data", command=self.show_data)

        # container for controlling plots
        top_frame = Frame(self.master)
        top_frame.pack(side=TOP, fill=BOTH, padx=10, pady=10)

        for i in [0, 1]:
            Grid.columnconfigure(top_frame, i, weight=1)
            Grid.rowconfigure(top_frame, i, weight=1)

        plots_label = Label(top_frame, text="Current plot:", anchor='w')
        plots_label.grid(row=0, column=0, padx=5, pady=5, sticky=N+S+E+W)

        self.plots_combobox = Combobox(top_frame, state="readonly")
        self.plots_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=N+S+E+W)
        self.plots_combobox.bind('<<ComboboxSelected>>', self.plots_combobox_selected)

        add_plot_button = Button(top_frame, text='Add new plot', command=self.add_new_plot)
        add_plot_button.grid(row=1, column=0, padx=5, pady=5, sticky=N+S+E+W)

        remove_plot_button = Button(top_frame, text='Remove current plot', command=self.remove_plot)
        remove_plot_button.grid(row=1, column=1, padx=5, pady=5, sticky=N+S+E+W)

        ttk.Separator(top_frame, orient=HORIZONTAL).grid(row=2, column=0, columnspan=2, pady=5, sticky=N + S + E + W)

        # container for switching frames
        self.container = Frame(self.master)
        self.container.pack(side=TOP, fill=BOTH, expand=True, padx=15)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.reset_plots()

    def show_plot(self):
        for plot in self.plots:
            plot.make_plot()
        plt.show()

    def reset_plots(self):
        """ Used after loading new file, removes all previous plots """
        self.plots_combobox['values'] = ["plot1"]
        self.plots_combobox.current(0)

        self.plots = [Plotter(parent=self.container, controller=self, name="plot1")]
        self.plots[0].grid(row=0, column=0, sticky="nsew")
        self.plots[0].tkraise()
        self.plot_counter = 2

    def plots_combobox_selected(self, event):
        """ Updates query parameters after another plot was selected in combobox """
        curr_plot_name = self.plots_combobox.get()
        curr_plot = next(x for x in self.plots if x.name == curr_plot_name)
        curr_plot.tkraise()

    def add_new_plot(self):
        """ Adds new plot to plots combobox """
        self.plots.append(Plotter(parent=self.container, controller=self, name=f"plot{self.plot_counter}"))
        counter = len(self.plots)
        self.plots[counter-1].grid(row=0, column=0, sticky="nsew")
        self.plots_combobox['values'] = (*self.plots_combobox['values'], self.plots[counter-1].name)
        self.plot_counter += 1
        self.plots_combobox.current(counter-1)
        self.plots[counter-1].tkraise()

    def remove_plot(self):
        """ Removes currently selected plot from plots combobox"""
        if len(self.plots) <= 1:
            return

        # remove plot
        curr_plot_name = self.plots_combobox.get()
        curr_plot = next(x for x in self.plots if x.name == curr_plot_name)
        self.plots.remove(curr_plot)
        self.plots[0].tkraise()

        # update combobox
        curr_values = list(self.plots_combobox['values'])
        curr_values.remove(curr_plot_name)
        self.plots_combobox['values'] = curr_values
        self.plots_combobox.current(0)

    def show_data(self):
        """ Shows the entire table for user to easily search through data """
        headers = self.database.get_columns()
        widths = [25 for x in range(len(headers))]
        generator = self.database.get_query('select * from data')
        show_table(headers, widths, generator)

    def load_from_text(self, extension):
        """ Asks user to choose file """
        f = filedialog.askopenfile(initialdir=os.getcwd(), title="Choose file with data",
                                   filetypes=((extension + " files", "*." + extension),))
        if f is None:
            return

        is_header, delimiter, success = show_import_form(f.name)

        if not success:
            messagebox.showinfo(message="Importing data was cancelled. Try again.")
            return

        types, success = show_types_form(f.name, f.readline(), is_header, delimiter)

        if not success:
            messagebox.showinfo(message="Importing data was cancelled. Try again.")
            return

        self.database.delete_database()
        self.database.load_to_db(f.name, is_header, delimiter, types)
        self.reset_plots()

    def exitProgram(self):
        self.master.destroy()


class Plotter(Frame):
    def __init__(self, parent, controller, name):
        Frame.__init__(self, parent)
        self.controller = controller
        self.name = name

        for i in range(3):
            Grid.columnconfigure(self, i, weight=1)
        for i in range(13):
            Grid.rowconfigure(self, i, weight=1)

        columns = ['', *list(self.controller.database.get_columns())]

        labels = ['Data:', 'Values:', 'Aggregate:', 'Where:', 'Group by:', 'Having:', 'Sort by:', '', 'Line color:', 'Marker:', 'Line style:']
        widgets_types = ['combobox', 'combobox', 'combobox', 'entry', 'combobox', 'entry', 'combobox', 'separator', 'combobox', 'combobox', 'combobox']
        custom_values = [[], [], ['', 'SUM', 'COUNT', 'AVG', 'MIN', 'MAX'], [], [], [], [], [], ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white'], ['', '.', ',', 'o', 'v', 's', 'p', '*', '+', 'x', 'X', '|', '_'], ['-', '--', '-.', ':']]
        self.widgets = []
        row_counter = 0

        for label, type_, values in zip(labels, widgets_types, custom_values):
            if type_ == 'combobox':
                Label(self, text=label, anchor='w').grid(row=row_counter, column=0, pady=5, sticky=N+S+E+W)
                new_widget = Combobox(self, values=columns if values == [] else values, state="readonly")
                new_widget.grid(row=row_counter, column=1, pady=5, sticky=N+S+E+W)
                new_widget.current(0)
                self.widgets.append(new_widget)
            elif type_ == 'entry':
                Label(self, text=label, anchor='w').grid(row=row_counter, column=0, pady=5, sticky=N+S+E+W)
                new_widget = StringVar(value='')
                Entry(self, textvariable=new_widget).grid(row=row_counter, column=1, pady=5, sticky=N+S+E+W)
                self.widgets.append(new_widget)
            elif type_ == 'separator':
                ttk.Separator(self, orient=HORIZONTAL).grid(row=row_counter, column=0, columnspan=2, pady=10,
                                                            sticky=N + S + E + W)

            row_counter += 1

        self.plot_button = Button(self, text='Plot!', command=self.show_plot)
        self.plot_button.grid(row=row_counter, column=0, columnspan=2, pady=5)

    def show_plot(self):
        self.controller.show_plot()

    def make_plot(self):
        """ Takes values from comboboxes and entries and makes plots """
        query_builder = QueryBuilder(
            self.widgets[0].get(),
            self.widgets[1].get(),
            self.widgets[2].get(),
            self.widgets[4].get(),
            self.widgets[5].get(),
            self.widgets[6].get(),
            self.widgets[3].get()
        )

        xs = []
        ys = []

        query = query_builder.build_query()
        if query == '':
            messagebox.showinfo(message="Nie zaznaczono danych!")
            return

        for row in self.controller.database.get_query(query):
            xs.append(row[0])
            ys.append(row[1])

        color_ = self.widgets[7].get() if self.widgets[7].get() != '' else 'None'
        marker_ = self.widgets[8].get() if self.widgets[8].get() != '' else 'None'
        line_style_ = self.widgets[9].get() if self.widgets[9].get() != '' else 'None'

        plt.plot(xs, ys, color=color_, marker=marker_, linestyle=line_style_)


if __name__ == "__main__":
    root = Tk()
    root.geometry("350x550")
    default_font = font.nametofont("TkFixedFont")
    default_font.configure(size=9)
    root.option_add("*Font", default_font)
    app = App(root)
    app.winfo_toplevel().title("Plotter")
    app.mainloop()
