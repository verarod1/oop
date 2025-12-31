import math
class Shape:
    def __init__(self):
        pass

    @property
    def area(self):
        return self.get_area()
    @property
    def perimeter(self):
        return self.get_perimeter()


class Triangle(Shape):

    def __init__(self, side1, side2, side3):
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3
        if self.is_exist()==False:
            raise Exception('Треугольник не существует')

    def is_exist(self):
        if self.side1>=self.side2+self.side3 or self.side2>=self.side3+self.side1 or self.side3>=self.side1+self.side2 or self.side1<=0 or self.side2<=0 or self.side3<=0:
            return False
        else:
            return True

    def get_perimeter(self):
        return (self.side1 + self.side2  + self.side3)

    def get_area(self):
        p=(self.side1+self.side2+self.side3)/2
        return math.sqrt(p*(p-self.side1)*(p-self.side2)*(p-self.side3))

    def get_type(self):
        max_side=max(self.side1, self.side2, self.side3)
        min_side=min(self.side1, self.side2, self.side3)
        if max_side**2==min_side**2+(sum([self.side1,self.side2,self.side3])-max_side-min_side)**2:
            return 'Треугольник прямоугольный'
        if max_side**2>min_side**2+(sum([self.side1,self.side2,self.side3])-max_side-min_side)**2:
            return 'Треугольник тупоугольный'
        if max_side**2<min_side**2+(sum([self.side1,self.side2,self.side3])-max_side-min_side)**2:
            return 'Треугольник остроугольный'

class Rectangle(Shape):
    def __init__(self, side1, side2):
        self.side1 = side1
        self.side2 = side2

    def get_perimeter(self):
        return(self.side1+self.side2)*2

    def get_area(self):
        return(self.side1*self.side2)

    def get_diagonal(self):
        return(math.sqrt((self.side1**2)+(self.side2**2)))

class Square(Rectangle):
    def __init__(self, side):
        self.side = side

    def get_perimeter(self):
        return(self.side*4)

    def get_area(self):
        return(self.side*self.side)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def get_perimeter(self):
        return(self.radius*2*math.pi)
    def get_area(self):
        return (self.radius*self.radius*math.pi)

    def diameter(self):
        return(2*self.radius)

circle = Circle(5)
print(f'Площадь круга равна {circle.area:.2f} ')
print(f'Периметр круга равен {circle.perimeter:.2f} ')
triangle = Triangle(3, 4, 5)
print(triangle.get_type())
