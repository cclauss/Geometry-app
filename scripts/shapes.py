from itertools import cycle

variable_letters = iter(cycle(['A', 'B', 'C', 'X', 'Y', 'Z']))
variable_num = 1


def get_variable_letter():
    global variable_num
    current_variable_letter = next(variable_letters)
    if current_variable_letter == 'Z':
        variable_num += 1
    return current_variable_letter + str(variable_num)


points = []
lines = []
angles = []


class Point:
    def __init__(self, x: int, y: int, create_text_command, delete_command, show: bool = True):
        self.x = x
        self.y = y
        for point_ in points:
            if point_.x == self.x and point_.y == self.y:
                raise ValueError('Point already exists.')
        self.name = get_variable_letter()
        self.coordinates = (self.x, self.y)
        self.create_text_command = create_text_command
        if show:
            self.text = self.create_text_command(self.x, self.y, text=self.name)
        self.displayed = show
        self.delete_command = delete_command
        self.blink = False

    def hide(self):
        if self.displayed:
            self.delete_command(self.text)
            self.displayed = False

    def show(self):
        if not self.displayed:
            self.text = self.create_text_command(self.x, self.y, text=self.name)
            self.displayed = True

    def set_coordinates(self, x: int, y: int):
        self.x = x
        self.y = y
        self.hide()
        self.show()

    def rename(self, new_name: str, refresh_command):
        if not new_name == self.name:
            for point_ in points:
                if point_.name == new_name:
                    raise ValueError(
                        f'A variable with the name {new_name} already exists. Please choose a different variable.'
                    )
            self.name = new_name
            self.hide()
            self.show()
            for line_ in lines:
                refresh_line(line_)
            refresh_command()

    def highlight(self):
        self.hide()
        self.text = self.create_text_command(self.x, self.y, text=self.name, fill='red')
        self.displayed = True

    def unhighlight(self):
        self.hide()
        if self.x and self.y:
            self.show()


class Line:
    def __init__(self, point1: Point, point2: Point, create_line_command, delete_command, show: bool = True):
        self.point1 = point1
        self.point2 = point2
        if self.point1 == self.point2:
            raise ValueError('A line must have two different points.')
        for line_ in lines:
            if (line_.point1 == point1 and line_.point2 == point2) or (line_.point2 == point1 and line_.point1 == point2):
                raise ValueError('Line already exists.')
        self.points = [point1, point2]
        self.name = point1.name + point2.name
        self.create_line_command = create_line_command
        if show:
            self.line = create_line_command(point1.x, point1.y, point2.x, point2.y)
        self.displayed = show
        self.delete_command = delete_command

    def hide(self):
        if self.displayed:
            self.delete_command(self.line)
            self.displayed = False

    def show(self):
        if not self.displayed:
            self.line = self.create_line_command(self.point1.x, self.point1.y, self.point2.x, self.point2.y)
            self.displayed = False

    def refresh(self):
        self.__init__(self.point1, self.point2, self.create_line_command, self.delete_command, self.displayed)

    def highlight(self, unhighlighted_others=False):
        if not unhighlighted_others:
            for angle_ in angles:
                angle_.unhighlight()
            for line_ in lines:
                line_.unhighlight()
        self.hide()
        self.line = self.create_line_command(self.point1.x, self.point1.y, self.point2.x, self.point2.y, fill='red')
        self.displayed = True

    def unhighlight(self):
        self.hide()
        if self.point1 and self.point2:
            self.show()


class Angle:
    def __init__(self, line1: Line, line2: Line):
        for angle in angles:
            if angle.lines == [line1, line2] or angle.lines == [line2, line1]:
                raise ValueError('Angle already exists')
        self.lines = [line1, line2]
        self.vertex = None
        for point1 in line1.points:
            for point2 in line2.points:
                if point1 == point2:
                    self.vertex = point1
        self.points = []
        for line in self.lines:
            for point in line.points:
                if not point in self.points and point != self.vertex:
                    self.points.append(point)
        self.name = f'{self.points[0].name}{self.vertex.name}{self.points[1].name}'
    
    def highlight(self):
        for angle_ in angles:
            angle_.unhighlight()
        for line_ in lines:
            line_.unhighlight()
        for line in self.lines:
            line.highlight(unhighlighted_others=True)
    
    def unhighlight(self):
        for line in lines:
            line.unhighlight()


def angle(line1: Line, line2: Line):
    angle_ = Angle(line1, line2)
    angles.append(angle_)
    return angle_


def refresh_angles():
    global angles
    angles = []
    for line1 in lines:
        for line2 in lines:
            if not line1 == line2:
                if line1.point1 == line2.point1 or line1.point1 == line2.point2 or line1.point2 == line2.point1 or line1.point2 == line2.point2:
                    try:
                        angle(line1, line2)
                    except ValueError:
                        pass


def point(x: int, y: int, create_text_command, delete_command, show_point: bool = True):
    point_ = Point(x, y, create_text_command, delete_command, show_point)
    points.append(point_)
    return point_


def delete_point(point_: Point):
    point_.x = None
    point_.y = None
    point_.hide()
    del points[points.index(point_)]


def line(point1: Point, point2: Point, create_line_command, delete_command, show: bool = True):
    line_ = Line(point1, point2, create_line_command, delete_command, show)
    lines.append(line_)
    refresh_angles()
    return line_


def delete_line(line_: Line):
    line_.point1 = None
    line_.point2 = None
    line_.hide()
    del lines[lines.index(line_)]
    refresh_angles()


def refresh_line(line_: Line):
    point1 = line_.point1
    point2 = line_.point2
    create_line_command = line_.create_line_command
    delete_command = line_.delete_command
    show = line_.displayed
    delete_line(line_)
    line(point1, point2, create_line_command, delete_command, show)


def get_point_by_coordinates(x: int, y: int):
    for point_ in points:
        if point_.x == x and point_.y == y:
            return point_


def get_point_by_name(name: str):
    for point_ in points:
        if point_.name == name:
            return point_


def get_line_by_name(name: str):
    for line_ in lines:
        if line_.name == name:
            return line_


def get_angle_by_name(name: str):
    for angle_ in angles:
        if angle_.name == name:
            return angle_
