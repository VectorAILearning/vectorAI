import {
  createAsyncThunk,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";
import axios from "../api/axiosInstance.ts";

interface meResponse {
  id: string;
  email: string;
  username: string;
}

interface UserState {
  id: string;
  username: string;
  password: string;
  email: string;
  avatar: string;
  subscription: boolean;
}
const initialState: UserState = {
  id: "",
  username: "",
  password: "",
  email: "",
  avatar: "",
  subscription: false,
};

export const me = createAsyncThunk<meResponse, void>("user/me", async () => {
  try {
    const response = await axios.get("/auth/me");
    return response.data;
  } catch (error) {
    console.log(error);
  }
});
const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setAvatar: (state, action: PayloadAction<string>) => {
      state.avatar = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(me.fulfilled, (state, action) => {
      state.username = action.payload.username;
      state.email = action.payload.email;
      state.id = action.payload.id;
    });
  },
});

// Экспортируем экшены и редьюсер
export const { setAvatar } = userSlice.actions;
export default userSlice.reducer;
