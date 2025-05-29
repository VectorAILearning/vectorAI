import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface SessionState {
  session_id: string | null;
}

const initialState: SessionState = {
  session_id: null,
};

export const sessionSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    setSessionId: (state, action: PayloadAction<string>) => {
      state.session_id = action.payload;
    },
  },
});

export const { setSessionId } = sessionSlice.actions;
export default sessionSlice.reducer;
