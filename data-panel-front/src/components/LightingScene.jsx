import React from "react";
import "./lightingScene.css"

export default function LightingScene(props) {
  return (
    <>
      {
        props.data && props.data.status[props.scene.id].enable ? 
          <div className="sceneCard">
            <div className="sceneMain">
              Escena
            </div>
            <hr className="sceneDivider"/>
            <div className="sceneSecond">              
              {props.scene.name}
            </div>  
          </div>
        : <></>
      }
      
    </> 
  )
}