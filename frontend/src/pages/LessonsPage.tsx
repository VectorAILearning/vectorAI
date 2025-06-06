import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import TextContent from "../components/TextContent";
import VideoContent from "../components/VideoContent"
import DialogContent from "../components/DialogContent";
import TestContent from "../components/TestContent";
import QuestionContent from "../components/QuestionContent";
import ReflectionContent from "../components/ReflectionContent";
import MistakesContent from "../components/MistakesContent";
import ExamplesContent from "../components/ExamplesContent"
import PracticeContent from "../components/PracticeContent"

export default function LessonsPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isCourseMenuOpen, setIsCourseMenuOpen] = useState(false);
  const [courses, setCourses] = useState<any[]>([]);
  const [statusCode, setStatusCode] = useState<number>(0);
  const [selectedCourse, setSelectedCourse] = useState<any | null>(null);
  const [selectedLessons, setSelectedLessons] = useState<any | null>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const courseMenuRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { lessonId, courseId } = useParams();

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
        setSelectedCourse(currentCourse || data[0]);
      })
      .catch((e) => console.log(e))
      .finally(() => setIsLoading(false));
  }, [courseId, navigate]);

  useEffect(() => {
    if (!courseId || !lessonId) return;
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/course/${courseId}/lesson/${lessonId}`)
      .then((res: any) => {
        if (!res.ok) throw new Error("Lesson not found");
        setStatusCode(res.status);
        return res.json();
      })
      .then((data) => {
        setSelectedLessons(data);
      })
      .catch(() => {
        const getFirstValidLesson = async () => {
          const apiHost = import.meta.env.VITE_API_HOST;
          const res = await fetch(`${apiHost}/api/v1/user-courses`);
          const data = await res.json();
          if (data.length === 0) {
            navigate(`/`, { replace: true });
            return;
          }
          const firstCourse = data[0];
          const modules = firstCourse.modules || [];
          const firstModule = modules[0];
          const lessons =
            firstModule && firstModule.lessons ? firstModule.lessons : [];
          const firstLesson = lessons[0];
          if (firstModule && firstLesson) {
            navigate(`/course/${firstCourse.id}/lesson/${firstLesson.id}`, {
              replace: true,
            });
          } else {
            navigate(`/course/${firstCourse.id}`, { replace: true });
          }
        };
        getFirstValidLesson();
      });
  }, [courseId, lessonId, navigate]);

  const getLessonId = (lessonId: any) => {
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/course/${courseId}/lesson/${lessonId}`)
      .then((res: any) => {
        setStatusCode(res.status);
        return res.json();
      })
      .then((data) => {
        setSelectedLessons(data);
        console.log(data)

      });

  };


  return (
    <div className="flex h-screen bg-base-100 text-lg">
      <header className="fixed top-0 left-0 right-0 h-17 bg-base-300 flex items-center px-4 z-50">
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
                    <Link key={course.id} to={`/course/${course.id}`}>
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
            {selectedCourse?.modules?.map((module: any, idx: number) => (
              <li key={idx}>
                <a className="text-lg font-semibold">{module.title}</a>
                <ul>
                  {module.lessons?.map((lesson: any, lidx: number) => (
                    <li key={lidx}>
                      <Link
                        to={`/course/${courseId}/lesson/${lesson.id}`}
                        className="text-base"
                        onClick={() => getLessonId(lesson.id)}
                      >
                        {lesson.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </aside>
      )}
      <main
        className="flex-1 bg-base-100 text-base-content flex justify-center overflow-y-auto"
        style={{ maxHeight: "90vh" }}
      >
        <div className="max-w-3xl w-full p-8">
          <>
            <h1 className="text-3xl font-bold mb-4 text-center">
              {selectedLessons?.title || selectedLessons?.detail}
            </h1>
            <p className="mb-8 text-base text-base-content/80 text-center">
              {selectedLessons?.description}
            </p>
            {selectedLessons?.contents && selectedLessons.contents.length > 0 && (
              <div className="mt-8">
                <h2 className="text-2xl font-semibold mb-4 text-center">Контент урока</h2>
                <ul className="space-y-4">
                  
                  {selectedLessons.contents.map((block: any, idx: number) => (
                    <li key={block.id || idx} className="p-4 rounded bg-base-200">
                      <div className="font-bold mb-1">
                        {block.position}. {block.type.toUpperCase()}   
                        <p></p>
                      </div>
                      {block.type === "text" && (
                        <TextContent
                        textContent={block.content}
                        />
                      )}
                      {block.type === "video" && (
                        <VideoContent
                        videoContent={block.content}
                        />
                      )}
                       {block.type === "examples" && (
                        <ExamplesContent
                        examplesContent={block.content}
                        />
                      )}
                      {block.type === "mistakes" && (
                       <MistakesContent
                        mistakesContent={block.content}
                       />
                      )}
                      {block.type === "dialog" && (
                        <DialogContent
                        dialogContent={block.content}
                        />
                      )}
                      {block.type === "practice" && (
                        <PracticeContent
                        practiceContent={block.content}
                        />
                      )}

                      {block.type === "open_answer" && (
                        <TestContent
                        testContent={block.content}
                        />
                      )}
                      {block.type === "reflection" && (
                        <ReflectionContent
                        reflectionContent={block.content}
                        />
                      )}
                      {block.type === "test" && (
                        <QuestionContent 
                        questionContent={block.content}
                        />
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        </div>
      </main>
    </div>
  );
}
