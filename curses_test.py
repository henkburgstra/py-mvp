import curses

def curses_init(mainwindow):
    subwin1 = mainwindow.subwin(2, 12, 0, 0)
    subwin1.addstr("Hello, World")
    subwin2 = mainwindow.subwin(2, 20, 2, 0)
    subwin2.addstr("Hello, World")
    mainwindow.refresh()
    subwin1.move(1, 4)
    while True:
        c = subwin1.getch()


curses.wrapper(curses_init)