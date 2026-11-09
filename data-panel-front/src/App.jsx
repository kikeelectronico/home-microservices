import './App.css';
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";
import Home from "./pages/home/Home.jsx"
import React, { useState } from "react";

const DEFAULT_BACKGROUND = '/black.png'

function App() {

  const [background_image, setBackgroundImage] = useState({url: DEFAULT_BACKGROUND, position: "0% 0%"});
  
  return (
    <div
      className="App"
      style={{ 
        backgroundImage: "url(" + (background_image.url ? background_image.url : DEFAULT_BACKGROUND )  + ")",
        backgroundPosition: background_image.position ? background_image.position : "0% 0%"
      }}
    >
      <div className="appOverlay"></div>
      <div className="appContent">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home setBackgroundImage={setBackgroundImage}/>} />
          </Routes>
        </BrowserRouter>
      </div>
    </div>
  );
}

export default App;
