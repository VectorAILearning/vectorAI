import React, { useCallback, useEffect, useRef } from "react";
import { me, setAvatar } from "../store/userSlice.ts";
import { useAppDispatch, useAppSelector } from "../store";

const UserProfilePage = () => {
  const dispatch = useAppDispatch();
  const { username, avatar, email } = useAppSelector((state) => state.user);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert("Файл слишком большой");
        return;
      }
      // Validate file type
      if (!file.type.startsWith("image/")) {
        alert("Можно загружать только изоброжение");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        dispatch(setAvatar(reader.result as string));
      };
      reader.readAsDataURL(file);
    },
    [],
  );

  useEffect(() => {
    dispatch(me());
  }, []);
  return (
    <div className="container max-w-2xl mx-auto py-8 mt-16">
      <div className="container max-w-2xl mx-auto py-8 rounded-2xl  border">
        <div className="flex items-center justify-center cursor-pointer">
          <div className="avatar" onClick={() => fileInputRef.current?.click()}>
            <div className="relative group ring-primary ring-offset-base-100 w-24 rounded-full ring-2 ring-offset-2 aspect-square">
              {avatar ? (
                <img
                  src={avatar}
                  className="w-full h-full object-contain"
                  alt="avatar"
                />
              ) : (
                <div className="avatar avatar-placeholder">
                  <div className="bg-gray-100 w-24 rounded-full">
                    <span className="text-3xl text-gray-700">
                      {username[0]}
                    </span>
                  </div>
                </div>
              )}
              <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="text-white text-center text-sm font-medium">
                  Поменять аватарку
                </div>
              </div>
            </div>
          </div>
          <input
            ref={fileInputRef}
            accept="image/*"
            className="hidden"
            type="file"
            onChange={handleFileSelect}
          />
        </div>
        <div className="text-center mt-10">
          <h3 className="font-semibold text-2xl">{username}</h3>
          <p className="textarea-lg mt-1 opacity-70">{email}</p>
          <div className="flex items-center justify-center mt-5">
            <div className="font-bold text-white bg-black rounded-full py-2 px-5">
              Premium Plan
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;
