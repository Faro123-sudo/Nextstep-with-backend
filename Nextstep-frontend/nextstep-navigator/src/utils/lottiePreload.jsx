import React, { createContext, useContext } from "react";
import Lottie from "lottie-react";

import looking from "../assets/animation/looking.json";
import manWalking from "../assets/animation/manWalking.json";
import contact from "../assets/animation/contact.json";
import forgotPassword from "../assets/animation/forgot-password.json";

const ANIMATIONS = Object.freeze({
  looking,
  manWalking,
  contact,
  forgotPassword,
});

const LottieContext = createContext(ANIMATIONS);

export function LottieProvider({ children }) {
  return <LottieContext.Provider value={ANIMATIONS}>{children}</LottieContext.Provider>;
}

export function useAnimation(name) {
  const map = useContext(LottieContext);
  return map?.[name];
}

export function isReady(name) {
  return !!ANIMATIONS[name];
}

export function waitFor(name) {
  return ANIMATIONS[name] ? Promise.resolve(ANIMATIONS[name]) : Promise.resolve();
}

export function LottieAnimation({ name, fallback = null, ...lottieProps }) {
  const data = useAnimation(name);
  if (!data) return fallback;
  return <Lottie animationData={data} {...lottieProps} />;
}
