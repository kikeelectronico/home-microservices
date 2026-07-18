import React from "react";
import "./shower.css"

export default function Shower(props) {
  return (
    <>
      {
        props.data && props.data.status.scene_ducha.enable ? 
          <div
            className="showerCard"
            // style={{boxShadow: "0 0.1rem 1rem rgba(" + (props.data.status["9339195d-75c3-4fc1-aeac-03f8af899e40_1"].on ? "255,0,0" : "0,0,0")  + ", 0.8)"}}
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