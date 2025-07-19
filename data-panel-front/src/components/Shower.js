import React from "react";
import "./shower.css"

export default function Shower(props) {
  return (
    <>
      {
        props.data && props.data.status.scene_ducha.enable ? 
          <div
            className="showerCard"
            // style={{boxShadow: "0 0.1rem 1rem rgba(" + (props.data.status.hue_12.on ? "255,0,0" : "0,0,0")  + ", 0.8)"}}
            style={{boxShadow: "0 0.1rem 1rem rgba(0,0,0,0.8)"}}
          >
            <div className="showerMain">
              Baño 
            </div>
            <hr className="showerDivider"/>
            <div className="showerSecond">
              {props.data.status.thermostat_bathroom.thermostatTemperatureAmbient} ºC
            </div>        
            <div className="showerSecond">
              {props.data.status.thermostat_bathroom.thermostatHumidityAmbient} %
            </div>        
          </div>
        : <></>
      }      
    </> 
  )
}