/**
 * Eagerly imports all Lottie animation JSON files so they are included in
 * the main bundle and parsed once at app startup, rather than being loaded
 * on-demand when individual components mount.
 *
 * Import this module as a side effect in App.jsx:
 *   import "./utils/lottiePreload";
 *
 * Then consume the cached animations from any component:
 *   import { animations } from "./utils/lottiePreload";
 *   <Lottie animationData={animations.looking} />
 */

export const animations = {};

// Preload animations in background without blocking main thread
Promise.all([
  import("../assets/animation/looking.json").then(mod => { animations.looking = mod.default; }),
  import("../assets/animation/manWalking.json").then(mod => { animations.manWalking = mod.default; }),
  import("../assets/animation/contact.json").then(mod => { animations.contact = mod.default; }),
  import("../assets/animation/forgot-password.json").then(mod => { animations.forgotPassword = mod.default; }),
]);
