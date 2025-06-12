import React, { useState, useRef, useEffect, use } from "react";
import { FaMoon, FaSun } from "react-icons/fa";
import { useNavigate, useParams, Link } from "react-router-dom";
import { FiRefreshCw } from "react-icons/fi";

const CoursePage: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isCourseMenuOpen, setIsCourseMenuOpen] = useState(false);
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<any | null>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const courseMenuRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  const navigate = useNavigate();
  const { courseId } = useParams();
  // Инициализация темы: если нет в localStorage — берём системную, сохраняем в localStorage
  function getInitialTheme(): "light" | "dark" {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
    const system = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    localStorage.setItem("theme", system);
    return system;
  }
  const [theme, setTheme] = useState<"light" | "dark">(getInitialTheme());

  useEffect(() => {
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/user-courses`)
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);

        if (data.length === 0) {
          navigate(`/`, { replace: true });
          return;
        }

        const currentCourse = data.find(
          (course: any) => course.id === courseId,
        );

        if (!courseId || !currentCourse) {
          navigate(`/course/${data[0].id}`, { replace: true });
          return;
        }

        setSelectedCourse(currentCourse);
      })
      .catch((e) => console.log(e))
      .finally(() => setIsLoading(false));
  }, [courseId, navigate]);

  console.log(isLoading);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setIsUserMenuOpen(false);
      }
      if (
        courseMenuRef.current &&
        !courseMenuRef.current.contains(event.target as Node)
      ) {
        setIsCourseMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  function handleRegenerateLesson(lessonId: string) {
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/lesson/${lessonId}/generate-content?force=true`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    alert("Урок в процессе перегенерации! Не нажимайте на кнопку снова!");
  }

  return (
    <div className="flex h-screen bg-base-100 text-lg">
      <header className="fixed top-0 left-0 right-0 h-16 bg-base-300 flex items-center px-4 z-50">
        <div className="flex items-center space-x-4 w-1/3">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="btn btn-ghost btn-circle"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
        {/* Course Title Dropdown - Centered Section */}
        <div className="flex items-center justify-center w-1/3">
          <div
            className="relative flex items-center gap-4 min-w-[600px] justify-center"
            ref={courseMenuRef}
          >
            <button className="btn btn-primary" onClick={() => navigate("/")}>
              Создать курс
            </button>
            <button
              onClick={() => setIsCourseMenuOpen(!isCourseMenuOpen)}
              className="btn btn-ghost flex items-center space-x-2"
              style={{ width: "fit-content", minWidth: 300 }}
            >
              <span className="text-xl">
                {selectedCourse?.title || (
                  <span className="loading loading-spinner loading-lg"></span>
                )}
              </span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
            {isCourseMenuOpen && (
              <div className="absolute top-full left-0 mt-2 min-w-[600px] w-fit bg-base-300 rounded-2xl shadow-lg z-50">
                <ul className="menu bg-base-300 p-2 text-xl">
                  {courses.map((course, idx) => (
                    <Link to={`/course/${course.id}`} key={course.id}>
                      <li>
                        <button
                          className="w-full text-left hover:bg-base-300 rounded p-2"
                          onClick={() => {
                            setSelectedCourse(course);
                            setIsCourseMenuOpen(false);
                          }}
                        >
                          <div className="flex items-center space-x-2">
                            <div>
                              <span className="font-semibold text-lg">
                                {course.title}
                              </span>
                              <p className="text-sm text-base-content/70">
                                {course.description}
                              </p>
                            </div>
                          </div>
                        </button>
                      </li>
                    </Link>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-4 justify-end w-1/3">
          <label className="flex cursor-pointer gap-2 items-center">
            <FaSun
              className={`transition-colors ${theme === "light" ? "text-yellow-400" : "text-gray-400"}`}
            />
            <input
              type="checkbox"
              className="toggle"
              checked={theme === "dark"}
              onChange={(e) => setTheme(e.target.checked ? "dark" : "light")}
              aria-label="Переключить тему"
            />
            <FaMoon
              className={`transition-colors ${theme === "dark" ? "text-blue-400" : "text-gray-400"}`}
            />
          </label>
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="btn btn-ghost flex items-center space-x-2"
            >
              <span>User Test</span>
              <span className="badge badge-primary">Pro</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
            {isUserMenuOpen && (
              <div className="absolute top-full right-0 mt-2 w-48 bg-base-200 rounded-lg shadow-lg">
                <ul className="menu bg-base-200 p-2">
                  <li>
                    <a className="text-base-content hover:bg-base-300">
                      Профиль
                    </a>
                  </li>
                  <li>
                    <a className="text-base-content hover:bg-base-300">Выход</a>
                  </li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </header>
      {isSidebarOpen && (
        <aside className="w-100 bg-base-200/90 p-1 overflow-y-auto text-base-content border-r border-base-300">
          {/* Sidebar content: Modules and Lessons */}
          <ul className="menu">
            {isLoading ? (
              <span className="loading loading-spinner loading-xl"></span>
            ) : (
              selectedCourse?.modules?.map((module: any, idx: number) => (
                <li key={idx}>
                  <a className="text-lg font-semibold">{module.title}</a>
                  <ul>
                    {module.lessons?.map((lesson: any, lidx: number) => (
                      <li key={lidx}>
                        <Link
                          to={`/course/${courseId}/lesson/${lesson.id}`}
                          className="text-base justify-between"
                        >
                          {lesson.title}
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
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              ))
            )}
          </ul>
        </aside>
      )}
      <main
        className="flex-1 mt-16 bg-base-100 text-base-content overflow-y-auto min-h-0 flex justify-center"
        style={{ minHeight: 0 }}
      >
        <div className="max-w-3xl w-full p-8">
          <h1 className="text-3xl font-bold mb-4 text-center">
            {selectedCourse?.title}
          </h1>
          <p className="mb-8 text-base text-base-content/80 text-center">
            {selectedCourse?.description}
          </p>
          {isLoading ? (
            <span className="loading loading-spinner loading-xl"></span>
          ) : (
            selectedCourse?.modules?.map((module: any, idx: number) => (
              <div
                key={idx}
                className="mb-10 text-left bg-base-200 rounded-xl p-6 shadow-sm"
              >
                <h2 className="text-xl font-semibold mb-2">{module.title}</h2>
                <p className="mb-3 text-base-content/70">
                  {module.description}
                </p>
                <ul className="list-disc ml-6">
                  {module.lessons?.map((lesson: any, lidx: number) => (
                    <li key={lidx} className="mb-1">
                      <span className="font-medium">{lesson.title}:</span>{" "}
                      {lesson.description}{" "}
                      <span className="text-xs text-base-content/50">
                        ({lesson.estimated_time_hours} ч)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>
        <button className="btn btn-neutral btn-lg fixed bottom-4 right-4 z-50">
          Чат с поддержкой
        </button>
      </main>
    </div>
  );
};

export default CoursePage;
