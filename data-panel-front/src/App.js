import './App.css';
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";
import Home from "./pages/home/Home.js"
import React, { useState } from "react";

function App() {

  const [background_image, setBackgroundImage] = useState({url: "./black.png", position: "0% 0%"});
  
  return (
    <div
      className="App"
      style={{ 
        backgroundImage: "url(" + (background_image.url ? background_image.url : "./black.png" )  + ")",
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
