import React from "react";
import "./room.css"

export default function Bathroom(props) {

    const thermostatMode = () => {
        var mode = props.home.status.thermostat_bathroom.thermostatMode
        if (mode === "heat") return "Calefacción"
        if (mode === "cool") return "Aire acondicionado"
        if (mode === "fan-only") return "Ventilador"
        if (mode === "off") return ""
    }

    const thermostatColor = () => {
        var mode = props.home.status.thermostat_bathroom.thermostatMode
        if (mode === "heat" && props.home.status.hue_12.on) return "255,0,0"
        else return "0,0,0"
    }

  return (
    props.home.status.scene_ducha.enable ?
        <div className="homeCard" style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
            <div className="homeCardTitle">
                Baño
            </div>
            <div className="homeCardRow" style={{marginTop: 5}}>
                <div className="roomCardAmbientContainer">
                    {props.home.status.thermostat_bathroom.thermostatTemperatureAmbient} ºC
                </div>
            </div>
            {
                thermostatMode() !== "" ?
                    <div className="homeCardRow homeCardRowNoBorder">
                        <div className="roomCardThermostatContainer">
                            {thermostatMode()}
                        </div>
                    </div>
                : <></>
            }
            {
                props.home.status.scene_ducha.enable ?
                    <div className="homeCardRow">
                        <div className="roomCardAlertContainer">
                            Modo ducha activo
                        </div>
                    </div>
                : <></>
            }
        </div>
    : <></>
    
    
  )
}