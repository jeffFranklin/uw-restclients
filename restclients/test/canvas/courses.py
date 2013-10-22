from django.test import TestCase
from restclients.canvas.courses import Courses


class CanvasTestCourses(TestCase):
    def test_course(self):
        with self.settings(
                RESTCLIENTS_CANVAS_DAO_CLASS='restclients.dao_implementation.canvas.File'):
            canvas = Courses()

            course = canvas.get_course(149650)

            self.assertEquals(course.course_id, 149650, "Has proper course id")
            self.assertEquals(course.course_url, "https://canvas.uw.edu/courses/149650", "Has proper course url")
            self.assertEquals(course.sis_course_id, "2012-summer-PHYS-121-A")
            self.assertEquals(course.sws_course_id(), "2012,summer,PHYS,121/A")
            self.assertEquals(course.account_id, 84378, "Has proper account id")
            self.assertEquals(course.term.sis_term_id, "2012-summer", "SIS term id")
            self.assertEquals(course.term.term_id, 810, "Term id")

    def test_courses(self):
        with self.settings(
                RESTCLIENTS_CANVAS_DAO_CLASS='restclients.dao_implementation.canvas.File'):
            canvas = Courses()

            courses = canvas.get_courses_in_account_by_sis_id(
                'uwcourse:seattle:arts-&-sciences:amath:amath',
                {'published': True})

            self.assertEquals(len(courses), 7, "Too few courses")

            course = courses[2]

            self.assertEquals(course.course_id, 141414, "Has proper course id")
            self.assertEquals(course.sis_course_id, "2013-spring-AMATH-403-A")
            self.assertEquals(course.sws_course_id(), "2013,spring,AMATH,403/A")
            self.assertEquals(course.name, "AMATH 403 A: Methods For Partial Differential Equations")
            self.assertEquals(course.account_id, 333333, "Has proper account id")
            self.assertEquals(course.course_url, "https://canvas.uw.edu/courses/141414", "Has proper course url")

    def test_published_courses(self):
        with self.settings(
                RESTCLIENTS_CANVAS_DAO_CLASS='restclients.dao_implementation.canvas.File'):
            canvas = Courses()

            courses = canvas.get_published_courses_in_account_by_sis_id(
                'uwcourse:seattle:arts-&-sciences:amath:amath')

            self.assertEquals(len(courses), 7, "Too few courses")

            course = courses[2]

            self.assertEquals(course.course_id, 141414, "Has proper course id")
            self.assertEquals(course.sis_course_id, "2013-spring-AMATH-403-A")
            self.assertEquals(course.sws_course_id(), "2013,spring,AMATH,403/A")
            self.assertEquals(course.name, "AMATH 403 A: Methods For Partial Differential Equations")
            self.assertEquals(course.account_id, 333333, "Has proper account id")
            self.assertEquals(course.course_url, "https://canvas.uw.edu/courses/141414", "Has proper course url")

    def test_courses_by_regid(self):
        with self.settings(
                RESTCLIENTS_CANVAS_DAO_CLASS='restclients.dao_implementation.canvas.File'):
            canvas = Courses()

            # Javerage's regid
            courses = canvas.get_courses_for_regid("9136CCB8F66711D5BE060004AC494FFE")

            self.assertEquals(len(courses), 1, "Has 1 canvas enrollment")

            course = courses[0]

            self.assertEquals(course.course_url, "https://canvas.uw.edu/courses/149650", "Has proper course url")
            self.assertEquals(course.sis_course_id, "2012-summer-PHYS-121-A")
            self.assertEquals(course.sws_course_id(), "2012,summer,PHYS,121/A")
            self.assertEquals(course.account_id, 84378, "Has proper account id")
