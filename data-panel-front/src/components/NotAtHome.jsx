import React from "react";
import "./notathome.css"

export default function NotAtHome(props) {
  return (
    <>
      {
        props.home && props.home.switch_at_home && !props.home.switch_at_home.on ? 
          <div className="notAtHomeCard">
            <div className="notAtHomeMain">
              Interruptor de presencia desactivado 
            </div>    
          </div>
        : <></>
      }
      
    </> 
  )
}