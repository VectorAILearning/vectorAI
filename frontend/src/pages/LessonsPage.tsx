import TextContent from "../components/lesson_content/TextContent";
import VideoContent from "../components/lesson_content/VideoContent";
import DialogContent from "../components/lesson_content/DialogContent";
import TestContent from "../components/lesson_content/TestContent";
import QuestionContent from "../components/lesson_content/QuestionContent";
import ReflectionContent from "../components/lesson_content/ReflectionContent";
import PracticeContent from "../components/lesson_content/PracticeContent";
import CodeContent from "../components/lesson_content/CodeContent";
import { useSelector } from "react-redux";

export default function LessonsPage() {
  const selectedLesson = useSelector(
    (state: any) => state.userCourses.selectedLesson,
  );

  return (
    <div className="max-w-3xl w-full">
      <div className="my-8 prose prose-md">
        <h1 className="mt-8 text-center">
          {selectedLesson?.title || selectedLesson?.detail}
        </h1>
        <p className="text-center">{selectedLesson?.description}</p>
      </div>

      {selectedLesson?.contents && selectedLesson.contents.length > 0 && (
        <>
          {selectedLesson.contents.map((block: any, idx: number) => (
            <div
              key={block.id || idx}
              className="relative bg-base-200 rounded-md p-6 prose prose-md mb-3"
            >
              <div className="absolute bottom-2 right-2 text-sm text-base-content/70 text-primary font-semibold">
                {block.type.toUpperCase()}
              </div>
              {block.type === "text" && (
                <TextContent textContent={block.content} />
              )}
              {block.type === "video" && (
                <VideoContent videoContent={block.content} />
              )}
              {block.type === "dialog" && (
                <DialogContent dialogContent={block.content} />
              )}
              {block.type === "practice" && (
                <PracticeContent practiceContent={block.content} />
              )}
              {block.type === "code" && (
                <CodeContent codeContent={block.content} />
              )}
              {block.type === "open_answer" && (
                <TestContent testContent={block.content} />
              )}
              {block.type === "reflection" && (
                <ReflectionContent reflectionContent={block.content} />
              )}
              {block.type === "test" && (
                <QuestionContent questionContent={block.content} />
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
