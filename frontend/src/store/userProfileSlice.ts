import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface UserState {
  username: string;
  password: string;
  email: string;
  avatar: string;
  subscription: boolean;
}
const initialState: UserState = {
  username: "Иван Иванов 1",
  password: "12345",
  email: "ivan.ivanov@example.com",
  avatar: "",
  subscription: false,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setAvatar: (state, action: PayloadAction<string>) => {
      state.avatar = action.payload;
    },
  },
});

// Экспортируем экшены и редьюсер
export const { setAvatar } = userSlice.actions;
export default userSlice.reducer;
