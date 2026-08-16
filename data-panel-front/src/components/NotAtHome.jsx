import React from "react";
import "./notathome.css"

export default function NotAtHome(props) {
  return (
    <>
      {
        props.data && !props.data.status.switch_at_home.on ? 
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