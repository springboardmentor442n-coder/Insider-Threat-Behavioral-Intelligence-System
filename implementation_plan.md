# Redesign Frontend to Professional UI

This plan outlines the steps to transform the current basic frontend into a professional, modern, and visually stunning web application for the Insider Threat Behavioral Intelligence System.

## User Review Required

> [!IMPORTANT]
> The redesign will introduce a **sleek dark mode** by default with vibrant accents, as this fits the "cybersecurity" and "intelligence system" theme very well. Please let me know if you prefer a light theme or a specific color palette.
> I will be using **Vanilla CSS** as per the best practices, avoiding external CSS frameworks to keep the project clean and maintainable.

## Open Questions

> [!NOTE]
> 1. Does the backend return specific string values like `"Threat"` or `"Normal"` for the prediction, or is it a numeric value? I will design the `ResultCard` to handle different states based on the prediction.
> 2. Are there any specific logos or branding you want to include in the header?

## Proposed Changes

We will systematically redesign the application by setting up a design system in CSS and creating reusable, beautiful React components.

---

### Global Styles & Assets

#### [MODIFY] index.css
- Import modern typography (e.g., 'Inter' from Google Fonts).
- Define a comprehensive CSS variables system (color palette, typography, spacing, shadows, border-radii).
- Implement a premium dark theme with glowing accents, glassmorphism effects, and smooth micro-animations.
- Add base styles for forms, inputs, and buttons.

#### [MODIFY] index.html
- Update the `<title>` and add meta tags for better SEO and presentation.

---

### Components

#### [MODIFY] src/components/PredictionForm.jsx
- Restructure the form into logical sections:
  - **Activity Metrics**: Device Connections, Emails Sent, Files Accessed, Websites Visited, Logon Count.
  - **Psychometric Profile (OCEAN)**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.
- Apply modern styling to inputs: hover effects, focus rings, and custom labels.
- Add a loading state to the submit button to provide feedback while the API is processing.

#### [MODIFY] src/components/ResultCard.jsx
- Implement a beautiful, animated card to display the prediction result.
- Use dynamic styling: e.g., a glowing red border/icon for a "Threat" prediction, and a calm green one for "Normal/Safe".

#### [MODIFY] src/App.jsx
- Wrap the application in a sleek layout consisting of a header (with title) and a main content area.
- Manage the layout to display the `PredictionForm` and `ResultCard` side-by-side on large screens, or stacked on smaller screens.

---

### Verification Plan

#### Automated Tests
- No automated tests exist currently, but I will ensure the React application compiles without errors (`npm run dev`).

#### Manual Verification
- Verify the UI renders correctly in the browser.
- Test form inputs for responsiveness and visual feedback (focus, hover).
- Submit a mock prediction and verify the `ResultCard` appears with the correct styling and animations.
