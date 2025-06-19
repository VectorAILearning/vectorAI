import { useAppDispatch, useAppSelector } from "../store";
import { useEffect } from "react";
import { me } from "../store/userSlice.ts";

export const useAuthUser = () => {
    const dispatch = useAppDispatch();
    const { token } = useAppSelector((state) => state.auth);
    const { id } = useAppSelector((state) => state.user);
    useEffect(() => {
        if (token && !id) {
            dispatch(me());
        }
    }, [dispatch, token, id]);
};
