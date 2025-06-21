import { Outlet } from "react-router-dom";
import Header from "../components/Header.tsx";

const MainLayout = () => {
  return (
    <div className="relative h-screen overflow-hidden pt-16">
      <Header />
      <Outlet />
    </div>
  );
};

export default MainLayout;
