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

const CourseLayout = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { courseId, lessonId } = useParams();
  useEffect(() => {
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/user-courses`)
      .then((res) => res.json())
      .then((data) => {
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
    <div className="relative h-screen overflow-hidden">
      <Header showCourseSelector={true} showSidebarToggle={true} />
      <div className="flex h-full">
        <CourseSidebar />
        <main className="flex w-full text-base-content overflow-y-auto justify-center">
          <Outlet />
        </main>
      </div>
      <ChatButton />
    </div>
  );
};

export default CourseLayout;
