import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../api/axiosInstance.ts";

export default function CourseRedirectPage() {
  const navigate = useNavigate();

  useEffect(() => {
    axiosInstance.get("/user-courses").then((res) => {
      const data = res.data;
      if (data.length > 0) {
        navigate(`/course/${data[0].id}`, { replace: true });
      } else {
        navigate(`/`, { replace: true });
      }
    });
  }, [navigate]);

  return null;
}
