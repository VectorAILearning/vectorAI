import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAppSelector } from "../store";
import { useTheme } from "../hooks/useTheme.ts";
import { FaMoon, FaSun } from "react-icons/fa";

interface HeaderProps {
  onLogin: () => void;
  onReset?: () => void;
}

export default function Header() {
  const location = useLocation().pathname;
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();

  const { username, avatar } = useAppSelector((state) => state.user);

  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const handleLogin = () => {
    navigate("/auth");
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <header className="w-full flex justify-between items-center p-4 bg-base-200">
      <div className="text-2xl font-bold text-primary">ВЕКТОР</div>
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
        {location == "/" && (
            <div className="flex gap-4">
              <button className="btn btn-primary" onClick={handleLogin}>
                Вход
              </button>
            </div>
        )}
        {location === "/courses" ||
          (location === "/profile" && (
            <div className="relative" ref={userMenuRef}>
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
                      <a className="text-base-content hover:bg-base-300">
                        Выход
                      </a>
                    </li>
                  </ul>
                </div>
              )}
            </div>
          ))}
      </div>
    </header>
  );
}
