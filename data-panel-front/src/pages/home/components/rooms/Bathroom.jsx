import React from "react";
import "./room.css"

export default function Bathroom(props) {

    const thermostatMode = () => {
        var mode = props.home.thermostat_bathroom?.thermostatMode
        if (mode === "heat") return "Calefacción"
        if (mode === "cool") return "Aire acondicionado"
        if (mode === "fan-only") return "Ventilador"
        if (mode === "off") return ""
    }

    const thermostatColor = () => {
        if (props.home) {
            var mode = props.home.thermostat_bathroom?.thermostatMode
            if (mode === "heat" && props.home["9339195d-75c3-4fc1-aeac-03f8af899e40_1"]?.on) return "255,0,0"
            else return "0,0,0"
        } else return "0,0,0"
    }

  return (
    props.home?.scene_ducha?.enable ?
        <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
            <div className="homeCardTitle">
                Baño
            </div>
            <div className="homeCardRow" style={{marginTop: 5}}>
                <div className={"roomCardAmbientContainer " + (props.home.thermostat_bathroom?.online ? "deviceOnline" : "deviceOffline")}>
                    {props.home.thermostat_bathroom?.thermostatTemperatureAmbient ?? "--.-"} ºC
                </div>
            </div>
            {
                props.home ?
                <>
                    {
                        thermostatMode() !== "" ?
                            <div className="homeCardRow homeCardRowNoBorder">
                                <div className="roomCardThermostatContainer deviceOnline">
                                    {thermostatMode()}
                                </div>
                            </div>
                        : <></>
                    }
                    {
                        props.home.scene_ducha.enable ?
                            <div className="homeCardRow">
                                <div className="roomCardAlertContainer deviceOnline">
                                    Modo ducha activo
                                </div>
                            </div>
                        : <></>
                    }
                </> : <></>
            }
        </div>
    : <></>
    
    
  )
}