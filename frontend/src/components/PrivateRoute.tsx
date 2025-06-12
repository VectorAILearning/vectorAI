import { useAppSelector } from "../store";
import { Navigate } from "react-router-dom";

export interface PrivateRouteProps {
  children: JSX.Element;
}
const PrivateRoute = ({ children }: PrivateRouteProps) => {
  const isAuth = useAppSelector((state) => state.auth.isAuth);
  if (!isAuth) {
    return <Navigate to="/auth" replace />;
  }
  return children;
};

export default PrivateRoute;
