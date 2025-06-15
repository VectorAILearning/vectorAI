import { Outlet, useNavigate, useParams } from "react-router-dom";
import Header from "../components/Header";
import ChatButton from "../components/ChatButton";
import CourseSidebar from "../components/CourseSidebar";
import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  setCourses,
  setSelectedCourse,
  setSelectedLesson,
} from "../store/userCoursesSlice";
import axiosInstance from "../api/axiosInstance.ts";

const CourseLayout = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { courseId, lessonId } = useParams();
  useEffect(() => {
    axiosInstance
      .get("/user-courses")
      .then((res) => {
        const data = res.data;
        dispatch(setCourses(data));
        if (data.length === 0) {
          navigate(`/`, { replace: true });
          return;
        }
        const currentCourse = data.find(
          (course: any) => course.id === courseId,
        );
        if (!courseId || !currentCourse) {
          navigate(`/course/${data[0].id}`, { replace: true });
          dispatch(setSelectedCourse(data[0]));
          return;
        }
        if (lessonId) {
          const currentLesson = currentCourse.modules
            .flatMap((module: any) => module.lessons)
            .find((lesson: any) => lesson.id === lessonId);
          if (!currentLesson) {
            navigate(`/course/${courseId}`, { replace: true });
            return;
          }
          dispatch(setSelectedLesson(currentLesson));
        }
        dispatch(setSelectedCourse(currentCourse));
      })
      .catch((e) => console.log(e));
  }, [dispatch, courseId, lessonId, navigate]);

  return (
    <>
      <Header showCourseSelector={true} showSidebarToggle={true} />
      <div className="flex h-screen overflow-hidden pt-16">
        <CourseSidebar />
        <main className="flex w-full text-base-content overflow-y-auto justify-center">
          <Outlet />
        </main>
        <ChatButton />
      </div>
    </>
  );
};

export default CourseLayout;
