import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl, pyqtSignal, Qt, QEventLoop
import os
import sqlite3
from random import choice


# чтение базы данных
def read_sql(request, *args):
    with sqlite3.connect('mov.sqlite') as conn:
        cursor = conn.cursor()
        return cursor.execute(request, args).fetchall()


# запись в базу данных
def write_sql(request, *args):
    with sqlite3.connect('mov.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute(request, args)


# проверка есть ли кароль на доске
def queen_is_true(color):
    for figs in field:
        for fig in figs:
            if isinstance(fig, Figure):
                if fig.get_color() == color and fig.get_typ() == 'queen':
                    return True
    return False


# проверка защищена фигура или нет
def isprotected(x, y):
    global field
    if isinstance(field[y][x], Figure):
        field[y][x].change_color()
        if (x, y) not in attact(field[y][x].get_insert_color()):
            field[y][x].change_color()
            return True
        field[y][x].change_color()
        return False
    return True


# итоговые возможные ходы с учетом всех правил
def itog_possible_moves(x, y):
    global field
    figure = field[y][x]
    possible = set(map(tuple, possib_move(x, y, figure)))
    if field[y][x].get_typ() == 'king':
        possible = set(map(tuple, possib_move(x, y, figure)))
        possible = {cord for cord in possible if isprotected(*cord)}
        field[y][x] = '*'
        att = attact(figure.get_insert_color())
        field[y][x] = figure
        return possible - att
    res = set()
    for i in possible:
        k1 = king_opend(x, y)
        k2 = king_closed(x, y, i[0], i[1])
        if k2 or k1:
            if isinstance(field[i[1]][i[0]], Figure):
                if field[i[1]][i[0]].get_typ() == 'king':
                    continue
                else:
                    res.add(i)
            res.add(i)
    return res


# подсветка шаха
def check_light():
    kings = set()
    for figs in field:
        for fig in figs:
            if isinstance(fig, Figure) and fig.get_typ() == 'king':
                kings.add(tuple(cords(fig)))
    for x, y in kings:
        if check_check(field[y][x].get_color()) == 'check':
            cors = cords_king(field[y][x].get_insert_color())
            label = QLabel(ex)
            pixmap = QPixmap(f"chess_progect/check.png")
            label.setPixmap(pixmap)
            label.move(int(50 + cors[0] * 100), 50 + 700 - 100 * cors[1])
            label.resize(pixmap.width(), pixmap.height())
            label.setScaledContents(False)
            label.setStyleSheet("background: transparent;")
            label.lower()
            label.show()
            if field[y][x].get_color() == 'black':
                ex.check_black = label
            else:
                ex.check_white = label
            break
        else:
            if ex.check_black:
                ex.check_black.deleteLater()
                ex.check_black = None
            if ex.check_white:
                ex.check_white.deleteLater()
                ex.check_white = None


# проверка мат/пат
def check_mate_or_stale_mate(color_of_moved):
    color_of_king = 'white' if color_of_moved == 'black' else 'black'
    cord = cords_king(color_of_king)
    if cord in attact(color_of_moved):
        for figs in field:
            for fig in figs:
                if isinstance(fig, Figure) and fig.get_color() == color_of_king:
                    if itog_possible_moves(*cords(fig)):
                        return 'continue'
        return 'mate'
    for figs in field:
        for fig in figs:
            if isinstance(fig, Figure) and fig.get_color() == color_of_king:
                if itog_possible_moves(*cords(fig)):
                    return 'continue'
    return 'draw'


# проверка есть ли на доске шах
def check_check(color_of_moved):
    color_of_king = 'white' if color_of_moved == 'black' else 'black'
    x, y = cords_king(color_of_king)
    if (x, y) in attact(color_of_moved):
        return 'check'


# проверка на шах/мат/пат
def checking(color_of_moved):
    mate_or_stale = check_mate_or_stale_mate(color_of_moved)
    font = QFont()
    font.setPointSize(80)
    if mate_or_stale == 'mate':
        print("Победа белых" if color_of_moved == 'white' else "Победа черных")
        # ex.create_end("Победа белых" if color_of_moved == 'white' else "Победа черных")
    elif mate_or_stale == 'draw':
        print("Ничья")
        # ex.create_end("Ничья")


# функция возвращает тип фигуры в зависимоти от номера выбора
def typ_of_fig(num):
    num = num if num <= 4 else num - 5
    if not num:
        typ = 'pawn'
    elif num == 1:
        typ = 'rook'
    elif num == 2:
        typ = 'knight'
    elif num == 3:
        typ = 'bishop'
    else:
        typ = 'queen'
    return typ


# функция выбора фигуры
def vibor(num, x, y, col=None, type_=None):
    global field
    if isinstance(field[y][x], Figure) and field[y][x].get_typ() == 'king':
        pass
    if isinstance(field[y][x], Figure):
        field[y][x].get_label().deleteLater()
    typ = typ_of_fig(num)
    color = col if col else 'black' if num <= 4 else 'white'
    label = QLabel(ex)
    pixmap = QPixmap(f"chess_progect/{color}/{typ}.png")
    label.setPixmap(pixmap)
    label.move(int(50 + x * 100), 50 + 100 * (7 - y) - 2)
    label.resize(pixmap.width(), pixmap.height())
    label.setScaledContents(False)
    label.setStyleSheet("background: transparent;")
    label.show()
    field[y][x] = Figure(label, typ, color)
    id_move = choice(list(set(range(1, 10000)) - set(map(lambda h: int(h[0]), read_sql('select id_move from moves')))))
    # write_sql(f"insert into moves (id, start, end, type_from, type_to, color, id_move) values(?, ?, ?, ?, ?, ?, ?)", ex.id, f"{x}{y}", f"{x}{y}", type_, typ, color, id_move)
    ex.set_order('white' if color == 'black' else 'black')
    checking(color)
    check_light()


# удаление label с доски
def delete(x, y):
    global field
    x, y = x, 900 - y
    x, y = (x - 50) // 100, (y - 50) // 100
    if x in range(8) and y in range(8):
        if isinstance(field[y][x], Figure) and not field[y][x].get_typ() == 'king':
            field[y][x].get_label().deleteLater()
            field[y][x] = '*'


# вохвращает короля в зависимости от цвета
def cords_king(color):
    for figs in field:
        for fig in figs:
            if isinstance(fig, Figure):
                if fig.get_color() == color and fig.get_typ() == 'king':
                    return cords(fig)


# проверка открыт ли будет король при ходе
def king_opend(x, y):
    global field
    figure = field[y][x]
    color = figure.get_color()
    insert_color = figure.get_insert_color()
    field[y][x] = '*'
    if cords_king(color) not in attact(insert_color):
        field[y][x] = figure
        return True
    field[y][x] = figure
    return False


# проверка будет ли закрык король при ходе
def king_closed(from_x, from_y, to_x, to_y):
    global field
    figure = field[from_y][from_x]
    figure_to = field[to_y][to_x]
    color = figure.get_color()
    insert_color = figure.get_insert_color()
    field[from_y][from_x], field[to_y][to_x] = '*', figure
    if cords_king(color) not in attact(insert_color):
        field[from_y][from_x], field[to_y][to_x] = figure, figure_to
        return True
    field[from_y][from_x], field[to_y][to_x] = figure, figure_to
    return False


# возвращает кординаты фигуры
def cords(fig):
    x, y = fig.get_label().x(), 800 - fig.get_label().y()
    x, y = (x - 50) // 100, (y - 50) // 100
    return x, y


# возвращает какие клетки под атакой от фигур конкретного цвета
def attact(color_attakers):
    res = set()
    for figs in field:
        for fig in figs:
            if isinstance(fig, Figure):
                if fig.get_color() == color_attakers:
                    x, y = cords(fig)
                    for i in possib_move(x, y, fig, mov_fight=False):
                        res.add(tuple(i))
    return res


# проверка бьет ли фигура другую фигуру
def fight(fig1, fig2):
    if isinstance(fig1, Figure) and isinstance(fig2, Figure):
        return fig1.get_color() != fig2.get_color()
    return True


# создает label
def make_label(filename, x, y):
    label = QLabel(ex)
    pixmap = QPixmap(filename)
    label.setPixmap(pixmap)
    label.move(int(50 + x * 100), 50 + 700 - 100 * y)
    label.resize(pixmap.width(), pixmap.height())
    label.setScaledContents(False)
    label.setStyleSheet("background: transparent;")
    label.lower()
    label.show()
    return label


# возвращает возможные ходы только с базовыми правилами
def possib_move(x, y, figur, mov_fight=True):
    name = figur.get_typ()
    if name == 'knight':
        return [
            [x1, y1]
            for x1 in [x - 1, x + 1, x - 2, x + 2] for y1 in [y - 1, y + 1, y - 2, y + 2]
            if abs(x - x1) != abs(y - y1) and x1 in range(8) and y1 in range(8) and (field[y1][x1] == '*' or
                                                                                     fight(field[y][x], field[y1][x1]))
        ]
    elif name == 'pawn':
        if figur.get_color() == 'black':
            y1 = y - 1
        else:
            y1 = y + 1
        res_list = []
        if y1 in range(8):
            for x1 in [i for i in [x - 1, x + 1] if i in range(8)]:
                if (isinstance(field[y1][x1], Figure) or not mov_fight) and fight(field[y][x], field[y1][x1]):
                    res_list.append([x1, y1])
            if not mov_fight:
                return res_list
            if field[y1][x] == '*':
                res_list.append([x, y1])
            if figur.get_color() == 'black' and y == 6 and field[4][x] == field[5][x] == '*':
                res_list.append([x, 4])
            if figur.get_color() == 'white' and y == 1 and field[3][x] == field[2][x] == '*':
                res_list.append([x, 3])
        return res_list
    elif name == 'rook':
        res_list = []
        for znak1 in [-1, 1, 0]:
            for znak2 in [-1, 1, 0]:
                if not znak1 or not znak2:
                    x1 = x + znak1
                    y1 = y + znak2
                    if x1 in range(8) and y1 in range(8):
                        while field[y1][x1] == '*':
                            res_list.append([x1, y1])
                            x1 = x1 + znak1
                            y1 = y1 + znak2
                            if not (x1 in range(8) and y1 in range(8)):
                                break
                        if y1 in range(8) and x1 in range(8):
                            if fight(field[y1][x1], field[y][x]):
                                res_list.append([x1, y1])
        return res_list
    elif name == 'bishop':
        res_list = []
        for znak1 in [-1, 1, 0]:
            for znak2 in [-1, 1, 0]:
                if znak1 and znak2:
                    x1 = x + znak1
                    y1 = y + znak2
                    if x1 in range(8) and y1 in range(8):
                        while field[y1][x1] == '*':
                            res_list.append([x1, y1])
                            x1 = x1 + znak1
                            y1 = y1 + znak2
                            if not (x1 in range(8) and y1 in range(8)):
                                break
                        if y1 in range(8) and x1 in range(8):
                            if fight(field[y1][x1], field[y][x]):
                                res_list.append([x1, y1])
        return res_list
    elif name == 'queen':
        return possib_move(x, y, Figure('', 'rook')) + possib_move(x, y, Figure('', 'bishop'))
    elif name == 'king':
        res_list = []
        color = figur.get_color()
        for znak1 in ['-', '+', '+ 1 -']:
            for znak2 in ['-', '+', '+ 1 -']:
                x1 = eval(f'{x} {znak1} 1')
                y1 = eval(f'{y} {znak2} 1')
                if x1 in range(8) and y1 in range(8):
                    if fight(field[y1][x1], field[y][x]):
                        res_list.append([x1, y1])
        if color == 'white':
            if x == 4 and y == 0 and isinstance(field[0][4], Figure):
                if isinstance(field[0][0], Figure):
                    if field[0][0].get_typ() == 'rook' and not field[0][0].get_mov() and not field[0][4].get_mov():
                        if field[0][1] == field[0][2] == field[0][3] == '*':
                            res_list.append([2, 0])
                if isinstance(field[0][7], Figure):
                    if field[0][7].get_typ() == 'rook' and not field[0][7].get_mov() and not field[0][4].get_mov():
                        if field[0][5] == field[0][6] == '*':
                            res_list.append([6, 0])
        elif color == 'black':
            if x == 4 and y == 7 and isinstance(field[7][4], Figure):
                if isinstance(field[7][0], Figure):
                    if field[7][0].get_typ() == 'rook' and not field[7][0].get_mov() and not field[7][4].get_mov():
                        if field[7][1] == field[7][2] == field[7][3] == '*':
                            res_list.append([2, 7])
                if isinstance(field[7][7], Figure):
                    if field[7][7].get_typ() == 'rook' and not field[7][7].get_mov() and not field[7][4].get_mov():
                        if field[7][5] == field[7][6] == '*':
                            res_list.append([6, 7])
        return res_list


# основной класс приложения
class Chess(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.effect = QSoundEffect()
        self.effect.setLoopCount(0)
        self.is_dragging = False
        self.is_deleting = False
        self.order_is_not_important = False
        self.for_move = None
        self.cords_from = None
        self.vib_is = True
        self.order = 'white'
        self.setFixedSize(900, 900)
        self.setStyleSheet("QWidget {background-image: url('chess_progect/field.png');background-repeat: no-repeat;"
                           "background-position: left;background-size: cover;}")
        self.restart = QPushButton('Рестарт', self)
        self.restart.setGeometry(350, 0, 100, 25)
        self.restart.clicked.connect(field.start)
        self.restart.setStyleSheet("background: none;")
        self.turn_order = QPushButton('Порядок ходов вкл', self)
        self.turn_order.setGeometry(450, 0, 150, 25)
        self.turn_order.clicked.connect(self.turn)
        self.turn_order.setStyleSheet("background: none;")
        self.possible_moves = set()
        self.check_black = None
        self.check_white = None
        self.mate_draw = None
        self.back_button = QPushButton("Назад", self)
        self.back_button.setGeometry(350, 25, 100, 20)
        self.back_button.clicked.connect(self.back)
        self.back_button.setStyleSheet("background: none;")
        if read_sql("select id from moves"):
            self.id = max(read_sql("select id from moves"))[0]
        else:
            self.id = 1
        # self.choice_game = QComboBox(self)
        # if read_sql("select id from moves"):
        #     self.choice_game.addItems(sorted({str(i[0]) for i in read_sql("select id from moves")}))
        # self.choice_game.setGeometry(450, 853, 100, 25)
        # self.choice_game.setStyleSheet("background: none;")
        # self.change_button = QPushButton('Выбрать', self)
        # self.change_button.setGeometry(450, 878, 100, 25)
        # self.change_button.clicked.connect(self.choice)
        # self.change_button.setStyleSheet("background: none;")
        self.delet_button = QPushButton('Удалить', self)
        self.delet_button.setGeometry(450, 25, 100, 20)
        self.delet_button.clicked.connect(self.delet)
        self.delet_button.setStyleSheet("background: none;")

    def delet(self):
        with sqlite3.connect('mov.sqlite') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM moves;")

    # def choice(self):
    #     if self.choice_game.currentText():
    #         field.start()
    #         id_game = int(self.choice_game.currentText())
    #         self.id = id_game
    #         result = read_sql("select start, end, type_from, type_to, color from moves where id = ?", self.id)[::-1]
    #         for i in result:
    #             from_cords, to_cords, type_from, type_to, color = i
    #             from_x, from_y = int(from_cords[0]), int(from_cords[1])
    #             to_x, to_y = int(to_cords[0]), int(to_cords[1])
    #             if type_to:
    #                 if type_from == 'None':
    #                     field[from_y][from_x] = Figure(make_label(f"chess_progect/{color}/{type_to}", from_x, from_y), type_to, color)
    #                     field[from_y][from_x] = '*'
    #                 else:
    #                     field[from_y][from_x].get_label().deleteLater()
    #                     field[from_y][from_x] = Figure(make_label(f"chess_progect/{color}/{type_to}", from_x, from_y), type_to, color)
    #             else:
    #                 field[to_y][to_x], field[from_y][from_x] = field[from_y][from_x], '*'
    #                 field[to_y][to_x].get_label().move(50 + to_x * 100, 50 + (7 - to_y) * 100)
    #                 self.order = field[to_y][to_x].get_insert_color()

    def back(self):
        moves = read_sql("select start, end, type_from, type_to, color, id_move from moves where id = ?", self.id)[::-1]
        moves = moves[0] if moves else None
        if moves:
            from_cords, to_cords, type_from, type_to, color, id_move = moves
            from_x, from_y = int(from_cords[0]), int(from_cords[1])
            to_x, to_y = int(to_cords[0]), int(to_cords[1])
            if type_to:
                if type_from == 'None':
                    field[from_y][from_x].get_label().deleteLater()
                    field[from_y][from_x] = '*'
                else:
                    field[from_y][from_x].get_label().deleteLater()
                    field[from_y][from_x] = Figure(make_label(f"chess_progect/{color}/{type_from}", from_x, from_y), type_to, color)
            # elif from_cords == to_cords:
            #     field[from_y][from_x] = Figure(make_label(f"chess_progect/{color}/{type_from}", from_x, from_y), type_to, color)
            else:
                field[from_y][from_x], field[to_y][to_x] = field[to_y][to_x], '*'
                field[from_y][from_x].get_label().move(50 + from_x * 100, 50 + (7 - from_y) * 100)
                self.order = field[from_y][from_x].get_color()
            # write_sql(f"delete from moves where id_move = {id_move}")

    def turn(self):
        if self.turn_order.text() == 'Порядок ходов вкл':
            self.turn_order.setText('Порядок ходов выкл')
            self.order_is_not_important = True
        else:
            self.turn_order.setText('Порядок ходов вкл')
            self.order_is_not_important = False

    def music(self, type_of_event):
        if type_of_event == 'move':
            self.effect.setSource(QUrl.fromLocalFile("chess_progect/music/move.wav"))
        self.effect.play()

    def mousePressEvent(self, event):
        x, y = event.position().x(), 900 - event.position().y()
        x, y = int((x - 50) // 100), int((y - 50) // 100)
        if event.button() == Qt.MouseButton.LeftButton:
            if x in range(8) and y in range(8):
                if isinstance(field[y][x], Figure):
                    label = field[y][x].get_label()
                    self.is_dragging = True
                    self.for_move = label
                    self.cords_from = [x, y]
                    possible = itog_possible_moves(x, y)
                    for i in possible:
                        label = QLabel(ex)
                        pixmap = QPixmap(f"chess_progect/possible_move.png")
                        label.setPixmap(pixmap)
                        label.move(int(50 + i[0] * 100), 50 + 700 - 100 * i[1])
                        label.resize(pixmap.width(), pixmap.height())
                        label.setScaledContents(False)
                        label.setStyleSheet("background: transparent;")
                        label.lower()
                        label.show()
                        self.possible_moves.add(label)
                    cursor_pos = event.position().toPoint()
                    self.for_move.move(int(cursor_pos.x() - 50), int(cursor_pos.y() - 50))
        if event.button() == Qt.MouseButton.MiddleButton:
            vibor(open_new_window(), x, y)
        if event.button() == Qt.MouseButton.RightButton:
            x, y = int(event.position().x()), 900 - int(event.position().y())
            x, y = (x - 50) // 100, (y - 50) // 100
            # if x in range(8) and y in range(8):
            #     fig = field[y][x]
            #     if isinstance(fig, Figure):
            #         id_move = choice(
            #             list(set(range(1, 10000)) - set(
            #                 map(lambda h: int(h[0]), read_sql('select id_move from moves')))))
            #         write_sql(f"insert into moves (id, start, end, type_from, color, id_move) values(?, ?, ?, ?, ?, ?)", self.id, f"{x}{y}", f"{x}{y}", fig.get_typ(), fig.get_color(), id_move)
            delete(int(event.position().x()), int(event.position().y()))

    def mouseMoveEvent(self, event):
        cursor_pos = event.position().toPoint()
        if self.is_dragging:
            self.for_move.move(int(cursor_pos.x() - 50), int(cursor_pos.y() - 50))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                cursor_pos = event.position().toPoint()
                x, y = int((int(cursor_pos.x()) - 50) // 100), int(((900 - int(cursor_pos.y())) - 50) // 100)
                x1, y1 = self.cords_from[0], self.cords_from[1]
                figur = field[y1][x1]
                check = itog_possible_moves(x1, y1)
                typ = figur.get_typ()
                color = figur.get_color()
                for i in self.possible_moves:
                    i.deleteLater()
                self.possible_moves = set()
                if not (x == x1 and y == y1) and (x, y) in check and (self.order == field[y1][x1].get_color() or
                                                                      self.order_is_not_important) and self.vib_is:
                    if isinstance(field[y][x], Figure) and field[y][x].get_typ() == 'king':
                        return
                    id_move = choice(
                        list(set(range(1, 10000)) - set(map(lambda h: int(h[0]), read_sql('select id_move from moves')))))
                    write_sql(f"insert into moves (id, start, end, type_from, id_move) values(?, ?, ?, ?, ?)", self.id, f"{x1}{y1}", f"{x}{y}", typ, id_move)
                    if not self.order_is_not_important:
                        self.order = 'black' if self.order == 'white' else 'white'
                    self.music('move')
                    if (typ == 'king' and color == 'white'
                            and x == 2 and y == 0 and not figur.get_mov()):
                        field[0][0].get_label().move(3 * 100 + 50, 800 - 50)
                        field[0][3], field[0][0] = field[0][0], '*'
                    elif (typ == 'king' and color == 'white'
                          and x == 6 and y == 0 and not figur.get_mov()):
                        field[0][7].get_label().move(5 * 100 + 50, 800 - 50)
                        field[0][5], field[0][7] = field[0][7], '*'
                    elif (typ == 'king' and color == 'black'
                          and x == 2 and y == 7 and not figur.get_mov()):
                        field[7][0].get_label().move(3 * 100 + 50, 50)
                        field[7][3], field[7][0] = field[7][0], '*'
                    elif (typ == 'king' and color == 'black'
                          and x == 6 and y == 7 and not figur.get_mov()):
                        field[7][7].get_label().move(5 * 100 + 50, 50)
                        field[7][5], field[7][7] = field[7][7], '*'
                    field[y1][x1].mov()
                    self.for_move.move(x * 100 + 50, 800 - (y * 100 + 50))
                    if isinstance(field[y][x], Figure):
                        field[y][x].get_label().deleteLater()
                    field[y][x], field[y1][x1] = field[y1][x1], '*'
                    if typ == 'pawn':
                        if color == 'white' and y == 7:
                            delete(int(cursor_pos.x()), int(cursor_pos.y()))
                            vibor(open_new_window(color), x, y, color, 'pawn')
                        if color == 'black' and y == 0:
                            delete(int(cursor_pos.x()), int(cursor_pos.y()))
                            vibor(open_new_window(color), x, y, color, 'pawn')
                    checking(field[y][x].get_color())
                    check_light()
                    # self.choice_game.clear()
                    # if read_sql("select id from moves"):
                    #     self.choice_game.addItems(sorted({str(i[0]) for i in read_sql("select id from moves")}))
                else:
                    self.for_move.move(x1 * 100 + 50, (7 - y1) * 100 + 50)

    def set_order(self, color):
        self.order = color


# класс основного поля игры
class Field:
    def __init__(self):
        self.field = []

    def start(self):
        if read_sql("select id from moves"):
            ex.id = max(read_sql("select id from moves"))[0] + 1
        else:
            ex.id = 1
        ex.check_black = None
        ex.check_white = None
        ex.vib_is = True
        ex.order = 'white'
        labels = ex.findChildren(QLabel)
        for label in labels:
            label.deleteLater()
        self.field = [['*' for _ in range(8)] for _ in range(8)]
        types_of_chess = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i in range(1, 3):
            color = 'black' if i == 1 else 'white'
            mn = 6 if color == 'white' else 1
            pos = 1 if mn == 6 else 6
            for j in range(8):
                label = make_label(f"chess_progect/{color}/{'pawn'}.png", 0, 0)
                label.move(int(50 + j * 100), 50 + 100 * mn)
                self.field[pos][j] = Figure(label, 'pawn', color)
        for i in range(8):
            label = make_label(f"chess_progect/{'black'}/{types_of_chess[i]}.png", 0, 0)
            label.move(int(50 + i * 100), 50)
            self.field[7][i] = Figure(label, types_of_chess[i], 'black')
        for i in range(8):
            label = make_label(f"chess_progect/{'white'}/{types_of_chess[i]}.png", 0, 0)
            label.move(int(50 + i * 100), 50 + 100 * 7 - 2)
            self.field[0][i] = Figure(label, types_of_chess[i])

    def __getitem__(self, item):
        return self.field[item]

    def __setitem__(self, key, value):
        self.field[key] = value


# класс окна для выбора фигуры
class NewWindow(QMainWindow):
    button_clicked = pyqtSignal(int)

    def __init__(self, color):
        super().__init__()
        self.initUI(color)

    def initUI(self, color, counter=None):
        self.setWindowTitle('Новое окно')
        a = "background-repeat: no-repeat; background-position: center; border: none; color: rgba(0, 0, 0, 0); }"
        sp = [
            f'chess_progect/{color}/{typ}.png'
            for color in ['black', 'white'] for typ in ['pawn', 'rook', 'knight', 'bishop', 'queen']
        ]
        if not color:
            counter = 0
            self.setFixedSize(500, 200)
            sp = [
                f'chess_progect/{color}/{typ}.png'
                for color in ['black', 'white'] for typ in ['pawn', 'rook', 'knight', 'bishop', 'queen']
            ]
            for j in sp:
                num = sp.index(j)
                if num <= 4:
                    size = num * 100
                    down = 0
                else:
                    size = (num - 5) * 100
                    down = 100
                button1 = QPushButton(f'Кнопка {counter}', self)
                button1.setGeometry(size, down, 100, 100)
                button1.clicked.connect(lambda _, counter=counter: self.on_button_clicked(counter))
                n = "QPushButton {background-image: url('" + j + "');"
                button1.setStyleSheet(n + a)
                counter += 1
        else:
            counter = 1
            self.setFixedSize(400, 100)
            sp = [
                f'chess_progect/{color}/{typ}.png' for typ in ['rook', 'knight', 'bishop', 'queen']
            ]
            for j in sp:
                num = sp.index(j)
                button1 = QPushButton(f'Кнопка {counter}', self)
                button1.setGeometry(num * 100, 0, 100, 100)
                button1.clicked.connect(lambda _, counter=counter: self.on_button_clicked(counter))
                n = "QPushButton {background-image: url('" + j + "');"
                button1.setStyleSheet(n + a)
                counter += 1

    def on_button_clicked(self, button_number):
        ex.vib_is = True
        self.button_clicked.emit(button_number)
        self.close()


# функция для выбора фигруы с использование окна из прошлого класса
def open_new_window(color=None):
    ex.vib_is = False
    ap = QApplication.instance()
    if ap is None:
        ap = QApplication(sys.argv)
    new_window = NewWindow(color)
    loop = QEventLoop()
    result = []

    def handle_button_clicked(button_number):
        result.append(button_number)
        loop.quit()
    new_window.button_clicked.connect(handle_button_clicked)
    new_window.show()
    loop.exec()
    return result[0]


class Figure:
    def __init__(self, label, typ='pawn', color='white'):
        self.moved = False
        self.typ = typ
        self.color = color
        self.label = label

    def __str__(self):
        return self.typ

    def __repr__(self):
        return self.typ

    def get_color(self):
        return self.color

    def get_label(self):
        return self.label

    def get_typ(self):
        return self.typ

    def mov(self):
        self.moved = True

    def get_mov(self):
        return self.moved

    def get_insert_color(self):
        return 'white' if self.color == 'black' else 'black'

    def change_color(self):
        self.color = 'white' if self.color == 'black' else 'black'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    field = Field()
    ex = Chess()
    field.start()
    ex.show()
    sys.exit(app.exec())
