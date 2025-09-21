import { useEffect } from "react";
import { refreshAccessToken } from "../utils/auth";

export const useAutoRefresh = () => {
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAccessToken(); // call correct function
    }, 14 * 60 * 1000); // every 14 minutes (before JWT usually expires)

    return () => clearInterval(interval);
  }, []);
};
