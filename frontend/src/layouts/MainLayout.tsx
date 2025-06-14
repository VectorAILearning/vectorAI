import { Outlet } from "react-router-dom";
import Header from "../components/Header.tsx";
import ChatButton from "../components/ChatButton.tsx";

const MainLayout = () => {
  return (
    <>
      <div className="relative h-screen overflow-hidden">
        <Header />
        <Outlet />
        <ChatButton />
      </div>
    </>
  );
};

export default MainLayout;
