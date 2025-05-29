import { useLocation, useNavigate } from "react-router-dom";
import { useAppSelector } from "../store";

interface HeaderProps {
  onLogin: () => void;
  onReset?: () => void;
}

export default function Header() {
  const location = useLocation().pathname == "/profile";
  const navigate = useNavigate();

  const { username, avatar } = useAppSelector((state) => state.user);

  const handleLogin = () => {
    navigate("/auth");
  };

  return (
    <header className="w-full flex justify-between items-center p-4 bg-base-200">
      <div className="text-2xl font-bold text-primary">ВЕКТОР</div>
      {!location && (
        <div className="flex gap-4">
          <button className="btn btn-primary" onClick={handleLogin}>
            Вход
          </button>
        </div>
      )}
      {location && (
        <div className="avatar">
          <div className="ring-primary ring-offset-base-100 w-5 rounded-full ring-2 ring-offset-2">
            {avatar ? (
              <img src={avatar} />
            ) : (
              <div className="flex items-center justify-center">
                <div>
                  <span>{username[0]}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
