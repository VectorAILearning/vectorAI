import { useAppSelector } from "../store";
import { Navigate } from "react-router-dom";
import type { PrivateRouteProps } from "./PrivateRoute.tsx";

const PublicRoute = ({ children }: PrivateRouteProps) => {
  const isAuth = useAppSelector((state) => state.auth.isAuth);

  if (isAuth) {
    return <Navigate to="/" replace />;
  }
  return children;
};

export default PublicRoute;
