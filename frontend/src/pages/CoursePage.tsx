import React from "react";
import { useSelector } from "react-redux";

const CoursePage: React.FC = () => {
  const selectedCourse =
    useSelector((state: any) => state.userCourses.selectedCourse) || null;

  return (
    <div className="max-w-3xl w-full p-8">
      <h1 className="text-3xl font-bold mb-4 text-center">
        {selectedCourse?.title}
      </h1>
      <p className="mb-8 text-base text-base-content/80 text-center">
        {selectedCourse?.description}
      </p>
      {selectedCourse?.modules?.map((module: any, idx: number) => (
        <div
          key={idx}
          className="mb-10 text-left bg-base-200 rounded-xl p-6 shadow-sm"
        >
          <h2 className="text-xl font-semibold mb-2">{module.title}</h2>
          <p className="mb-3 text-base-content/70">{module.description}</p>
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
      ))}
    </div>
  );
};

export default CoursePage;
