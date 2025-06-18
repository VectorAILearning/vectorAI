import TextContent from "../components/lesson_content/TextContent";
import VideoContent from "../components/lesson_content/VideoContent";
import DialogContent from "../components/lesson_content/DialogContent";
import TestContent from "../components/lesson_content/TestContent";
import QuestionContent from "../components/lesson_content/QuestionContent";
import ReflectionContent from "../components/lesson_content/ReflectionContent";
import PracticeContent from "../components/lesson_content/PracticeContent";
import CodeContent from "../components/lesson_content/CodeContent";
import { useSelector } from "react-redux";

function LessonBlock({ block }: { block: any }) {
  switch (block.type) {
    case "text":
      return <TextContent textContent={block.content} />;
    case "video":
      return <VideoContent videoContent={block.content} />;
    case "dialog":
      return <DialogContent dialogContent={block.content} />;
    case "practice":
      return <PracticeContent practiceContent={block.content} />;
    case "code":
      return <CodeContent codeContent={block.content} />;
    case "open_answer":
      return <TestContent testContent={block.content} />;
    case "reflection":
      return <ReflectionContent reflectionContent={block.content} />;
    case "test":
      return <QuestionContent questionContent={block.content} />;
    default:
      return null;
  }
}

export default function LessonsPage() {

const selectedLesson = useSelector(
    (state: any) => state.userLessons.selectedLessons || null,
  );
  const error = useSelector(
    (state: any) => state.userLessons.error || null,
  );
  const loading = useSelector(
    (state: any) => state.userLessons.loading || null,
  );
  return (
    <div className="max-w-3xl w-full">
      <div>  
        
          {loading === "succeeded" ? <div>
        <div className="my-8 prose prose-md mx-auto text-center">
         <h1>{selectedLesson?.title || selectedLesson?.detail}</h1>
         <p>{selectedLesson?.description}</p>
        </div>
      
      {selectedLesson?.contents && selectedLesson.contents.length > 0 && (
        <>
          {selectedLesson.contents.map((block: any, idx: number) => (
            <div
              key={block.id || idx}
              className="relative bg-base-200 rounded-md p-5 mb-3"
            >
              <div className="prose prose-md mx-auto">
                <LessonBlock block={block} />
              </div>
              <div className="absolute bottom-2 right-2 text-sm text-base-content/70 text-primary font-semibold">
                {block.type.toUpperCase()}
              </div>
            </div>
          ))}
        </>
      )}
      </div> 
      : loading === "failed"
       ? error 
       : 
      <div className="my-8 prose prose-md mx-auto text-center">
          <span className="loading loading-spinner loading-xl"></span>
      </div> }
      
      
      </div>
      
    </div>
  );
}
