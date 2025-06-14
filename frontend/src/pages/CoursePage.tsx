import React from "react";
import { useSelector } from "react-redux";

const CoursePage: React.FC = () => {
  const selectedCourse =
    useSelector((state: any) => state.userCourses.selectedCourse) || null;

  return (
    <div className="max-w-3xl w-full mx-auto">
      <div className="prose prose-md text-center my-8">
        <h1>{selectedCourse?.title}</h1>
        <p>{selectedCourse?.description}</p>
      </div>
      {selectedCourse?.modules?.map((module: any, idx: number) => (
        <div
          key={idx}
          className="mb-3 bg-base-200 rounded-md p-5 prose prose-md"
        >
          <h2>{module.title}</h2>
          <p>{module.description}</p>
          <ul>
            {module.lessons?.map((lesson: any, lidx: number) => (
              <li key={lidx}>
                <span>{lesson.title}:</span> {lesson.description}
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
