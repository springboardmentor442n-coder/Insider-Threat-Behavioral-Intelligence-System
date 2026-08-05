import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

import App from "./App";
import queryClient from "./config/queryClient";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          richColors
          position="top-right"
          closeButton
          expand
          duration={4000}
        />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
