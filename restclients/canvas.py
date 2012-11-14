"""
This is the interface for interacting with Instructure's Canvas web services.
"""

from restclients.dao import Canvas_DAO
from restclients.models import CanvasEnrollment, CanvasCourse
from restclients.exceptions import DataFailureException
import json
import re


class Canvas(object):
    """
    Get book information for courses.
    """

    def get_courses_for_regid(self, regid):
        dao = Canvas_DAO()

        url = "/api/v1/courses.json?as_user_id=sis_user_id:%s" % (regid)
        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        courses = []

        for section in data:
            course_id = section["id"]
            course_info = self._get_course_info_by_canvas_id(course_id)

            if course_info["sis_course_id"] is not None:
                course_url = section["calendar"]["ics"]
                course_url = re.sub(r"(.*?[a-z]/).*", r"\1", course_url)
                course_url = "%scourses/%s" % (course_url, course_id)

                course = CanvasCourse()
                course.course_url = course_url
                course.course_name = course_info["name"]
                course.sis_id = course_info["sis_course_id"]

                courses.append(course)

        return courses

    def get_enrollments_for_regid(self, regid):
        dao = Canvas_DAO()

        url = "/api/v1/users/sis_user_id:%s/enrollments" % (regid)

        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        enrollments = []
        for section in data:
            course_id = section["course_id"]
            course_info = self._get_course_info_by_canvas_id(course_id)

            if course_info["sis_course_id"] is not None:
                user_url = section["html_url"]
                course_url = re.sub("/users/.*", "", user_url)
                enrollment = CanvasEnrollment()
                enrollment.course_url = course_url
                enrollment.course_name = course_info["name"]
                enrollment.sis_id = course_info["sis_course_id"]

                enrollments.append(enrollment)
        return enrollments

    def _get_course_info_by_canvas_id(self, canvas_id):
        dao = Canvas_DAO()

        url = "/api/v1/courses/%s" % (canvas_id)

        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        return data
        print data["name"]
        print data["sis_course_id"]