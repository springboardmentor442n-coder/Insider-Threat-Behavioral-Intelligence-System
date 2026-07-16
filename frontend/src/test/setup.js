import '@testing-library/jest-dom';

// jsdom has no canvas, and Chart.js calls getContext on mount. We do not test
// the rendered pixels (that is Playwright's job, against a real browser), so a
// no-op stub keeps the console clean without changing what we assert.
HTMLCanvasElement.prototype.getContext = () => null;

// Chart.js also calls these on the canvas parent; stub to no-ops.
window.matchMedia = window.matchMedia || function () {
  return { matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} };
};
