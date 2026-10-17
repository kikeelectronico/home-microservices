import React from "react";
import "./thermostat.css"

export default function Thermostat(props) {

  const thermostatMode = () => {
    var mode = props.data.status.thermostat_livingroom.thermostatMode
    if (mode === "heat") return "Calor"
    if (mode === "cool") return "Frío"
    if (mode === "fan-only") return "Ventilador"
    if (mode === "off") return "Apagado"
  }

  const getColor = () => {
    var mode = props.data.status.thermostat_livingroom.thermostatMode
    if (mode === "heat" && props.data.status["fecf95fe-7cf3-4cc1-87bc-98e5669320f8_1"].on) return "255,0,0"
    else if (mode === "cool" && props.data.status.ac_001.on) return "0,0,255"
    else if (mode === "fan-only" && props.data.status.ac_001.on) return "255,255,255"
    else return "0,0,0"
  }

  return (
    <>
      <div
        className="thermostatCard"
        style={{boxShadow: "0 0.1rem 1rem rgba(" + getColor() + ", 0.8)"}}
      >
        <div className="thermostatTemperature">
          {props.data.status.thermostat_livingroom.thermostatTemperatureAmbient} ºC
        </div>
        <hr className="thermostatDivider"/>
        <div className="thermostatStatus">
          {thermostatMode()}
        </div>      
      </div>
    </> 
  )
}