import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function CourseRedirectPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const apiHost = import.meta.env.VITE_API_HOST;
    fetch(`${apiHost}/api/v1/user-courses`)
      .then((res) => res.json())
      .then((data) => {
        if (data.length > 0) {
          navigate(`/course/${data[0].id}`, { replace: true });
        } else {
          navigate(`/`, { replace: true });
        }
      });
  }, [navigate]);

  return null;
}
