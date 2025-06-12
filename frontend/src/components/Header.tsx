import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store";
import { useTheme } from "../hooks/useTheme.ts";
import { FaMoon, FaSun } from "react-icons/fa";
import { useSelector } from "react-redux";
import { toggleSidebar } from "../store/uiSlice.ts";
import { setSelectedCourse } from "../store/userCoursesSlice.ts";
import { FiMenu } from "react-icons/fi";

interface HeaderProps {
  showCourseSelector?: boolean;
  showSidebarToggle?: boolean;
}

export default function Header({
  showCourseSelector = false,
  showSidebarToggle = false,
}: HeaderProps) {
  const location = useLocation().pathname;
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const { theme, setTheme } = useTheme();
  const { username, avatar } = useAppSelector((state) => state.user);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogin = () => {
    navigate("/auth");
  };

  const courses = showCourseSelector
    ? useSelector((state: any) => state.userCourses.courses || [])
    : [];
  const selectedCourse = showCourseSelector
    ? useSelector((state: any) => state.userCourses.selectedCourse || null)
    : null;

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <header className="w-full flex justify-between items-center p-3 bg-base-300">
      <div className="flex items-center gap-2">
        {showSidebarToggle && (
          <button
            className="btn btn-ghost btn-circle"
            onClick={() => dispatch(toggleSidebar())}
          >
            <FiMenu className="w-6 h-6" />
          </button>
        )}
        <div
          className="text-2xl font-bold text-primary cursor-pointer"
          onClick={() => navigate("/")}
        >
          ВЕКТОР
        </div>
      </div>
      {showCourseSelector && (
        <div className="flex items-center justify-center">
          <button className="btn btn-primary" onClick={() => navigate("/")}>
            Создать курс
          </button>
          <select
            className="ml-2 select"
            value={selectedCourse?.id || ""}
            onChange={(e) => {
              const course = courses.find((c: any) => c.id === e.target.value);
              dispatch(setSelectedCourse(course));
              navigate(`/course/${course.id}`);
            }}
          >
            {courses.map((course: any) => (
              <option key={course.id} value={course.id}>
                {course.title}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className="flex items-center justify-end">
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
        {location == "/" && (
          <div className="flex gap-4">
            <button className="btn btn-primary" onClick={handleLogin}>
              Вход
            </button>
          </div>
        )}
        <div className="relative">
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="btn btn-ghost flex items-center space-x-2"
          >
            <div className="avatar">
              <div className="ring-primary ring-offset-base-100 w-5 rounded-full ring-2 ring-offset-2">
                {avatar ? (
                  <img src={avatar} />
                ) : (
                  <div className="flex items-center justify-center">
                    <div>
                      <span>{username[0]}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
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
              <ul
                className="menu bg-base-200 p-2"
                onClick={() => setIsUserMenuOpen(false)}
              >
                <li>
                  <Link
                    to="/profile"
                    className="text-base-content hover:bg-base-300"
                  >
                    Профиль
                  </Link>
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
  );
}
