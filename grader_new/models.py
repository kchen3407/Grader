import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('social.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    is_teacher = BooleanField()
    is_parent = BooleanField()
    is_student = BooleanField()
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        
    @classmethod
    def create_user(cls, username, email, password, 
                    teacher=False, parent=False, student=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_teacher=teacher, is_parent=parent,
                    is_student=student)
        except IntegrityError:
            raise ValueError("User already exists")
    

class Course(Model):
    teacher = ForeignKeyField(User, backref='teaches')
    student = ManyToManyField(User, backref='courses')
    time = CharField(max_length=300)
    name = CharField(unique = True, max_length=100)
    description = TextField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_course(cls, teacher,time, 
                    name, description):
        try:
            #with DATABASE.transaction():
            cls.create(
                teacher=teacher,
                time=time,
                name=name,
                description=description)
        except IntegrityError:
            raise ValueError("Course already exists")
    
StudentCourse = Course.student.get_through_model()

class Assignment(Model):
    name = CharField(unique = True, max_length=100)
    course = ForeignKeyField(Course, backref='assignments')

    class Meta:
        database = DATABASE
    
    @classmethod
    def create_assignment(cls,name,course):
        try:
            with DATABASE.transaction():
                cls.create(
                    name=name,
                    course=course
                )
        except IntegrityError:
            raise ValueError("Assignment already exists")
        
class Grade(Model):
    student = ForeignKeyField(User, related_name='student_course')
    letter = CharField(max_length=2)
    assignement = ForeignKeyField(Assignment, related_name='assignment')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Course, Assignment,StudentCourse], safe=True)
    DATABASE.close()