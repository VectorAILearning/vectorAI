import { Link } from "react-router-dom";
import { FiRefreshCw } from "react-icons/fi";
import Tippy from "@tippyjs/react";
import { useSelector } from "react-redux";
import axiosInstance from "../api/axiosInstance";

const CourseSidebar = () => {
  const selectedCourse = useSelector(
    (state: any) => state.userCourses.selectedCourse || null,
  );
  const isSidebarOpen = useSelector((state: any) => state.ui.isSidebarOpen);

  function handleRegenerateLesson(lessonId: string) {
    axiosInstance.post(`/lesson/${lessonId}/generate-content?force=true`);
    alert("Урок в процессе перегенерации! Не нажимайте на кнопку снова!");
  }

  return (
    <aside
      className={`w-1/4 bg-base-200 p-2 overflow-y-auto text-base-content ${isSidebarOpen ? "block" : "hidden"}`}
    >
      <ul className="menu">
        {selectedCourse?.modules?.map((module: any, idx: number) => (
          <li key={idx}>
            <a className="text-lg font-semibold">{module.title}</a>
            <ul>
              {module.lessons?.map((lesson: any, lidx: number) => (
                <li key={lidx}>
                  <Link
                    to={`/course/${selectedCourse.id}/lesson/${lesson.id}`}
                    className="text-base justify-between"
                  >
                    {lesson.title}
                    <Tippy content="Перегенерировать урок">
                      <button
                        className="btn btn-ghost btn-xs w-8 h-8"
                        title="Перегенерировать урок"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleRegenerateLesson(lesson.id);
                        }}
                      >
                        <FiRefreshCw className="w-4 h-4" />
                      </button>
                    </Tippy>
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default CourseSidebar;
