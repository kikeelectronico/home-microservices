import React from "react";
import "./room.css"

export default function Bedroom(props) {

    const thermostatMode = () => {
        var mode = props.home.status.thermostat_dormitorio.thermostatMode
        if (mode === "heat") return "Calefacción"
        if (mode === "cool") return "Aire acondicionado"
        if (mode === "fan-only") return "Ventilador"
        if (mode === "off") return ""
    }

    const thermostatColor = () => {
        var mode = props.home.status.thermostat_dormitorio.thermostatMode
        if (mode === "heat" && props.home.status.hue_8.on) return "255,0,0"
        else return "0,0,0"
    }

  return (
    <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
        <div className="homeCardTitle">
            Dormitorio
        </div>
        <div className="homeCardRow" style={{marginTop: 5}}>
            <div className="roomCardAmbientContainer">
                {props.home.status.thermostat_dormitorio.thermostatTemperatureAmbient} ºC
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
            props.home.status["e6c2e2bd-5057-49bc-821f-a4b10e415ac6"].openPercent === 100 ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Ventana abierta
                    </div>
                </div>
            : <></>
        }
        {
            props.home.status["e6c2e2bd-5057-49bc-821f-a4b10e415ac6"].openPercent === 100 && 
            props.home.status.thermostat_livingroom.thermostatMode === "cool" ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Cierra la ventana
                    </div>
                </div>
            : <></>
        }
    </div>
  )
}