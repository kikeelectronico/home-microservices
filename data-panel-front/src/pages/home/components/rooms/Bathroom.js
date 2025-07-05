import React, { useState, useEffect } from "react";
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
        <div className="homeCard homeCardTopPadding" style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
            <div className="roomCardTitle">
                Baño
            </div>
            <div className="roomCardRow" style={{marginTop: 5}}>
                <div className="roomCardAmbientContainer">
                    {props.home.status.thermostat_bathroom.thermostatTemperatureAmbient} ºC
                </div>
            </div>
            <div className="roomCardRow no-border" style={{marginBottom: 10}}>
                <div className="roomCardThermostatContainer">
                    {thermostatMode()}
                </div>
            </div>
            {
                props.home.status.scene_ducha.enable ?
                    <div className="roomCardRow">
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