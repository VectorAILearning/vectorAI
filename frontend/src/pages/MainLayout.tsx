import { Outlet } from "react-router-dom";
import Header from "../components/Header.tsx";
import ChatButton from "../components/ChatButton.tsx";

const MainLayout = () => {
  return (
    <>
      <div className="relative h-screen overflow-hidden">
        <div className="fixed top-0 left-0 w-full h-16 bg-white shadow z-10">
          <Header />
        </div>
        <div className="pt-17">
          <Outlet />
        </div>
        <div>
          <ChatButton />
        </div>
      </div>
    </>
  );
};

export default MainLayout;
