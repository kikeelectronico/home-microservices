import React from "react";
import "./bedroom.css"

export default function Bedroom(props) {
  return (
    <>
      {
        props.data && 
        ( props.data.status.hue_6.on || props.data.status.rgb003.on ) ? 
          <div className="bedroomCard">
            <div className="bedroomMain">
              Dormitorio 
            </div>    
          </div>
        : <></>
      }
      
    </> 
  )
}