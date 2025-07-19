import React from "react";
import "./room.css"

export default function Livingroom(props) {

    const thermostatMode = () => {
        var mode = props.home.status.thermostat_livingroom.thermostatMode
        if (mode === "heat") return "Calefacción"
        if (mode === "cool") return "Aire acondicionado"
        if (mode === "fan-only") return "Ventilador"
        if (mode === "off") return ""
    }

    const thermostatColor = () => {
        var mode = props.home.status.thermostat_livingroom.thermostatMode
        if (mode === "heat" && props.home.status.hue_8.on) return "255,0,0"
        else if (mode === "cool" && props.home.status.ac_001.on) return "0,0,255"
        else if (mode === "fan-only" && props.home.status.ac_001.on) return "255,255,255"
        else return "0,0,0"
    }

  return (
    <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
        <div className="homeCardTitle">
            Salón
        </div>
        <div className="homeCardRow" style={{marginTop: 5}}>
            <div className="roomCardAmbientContainer">
                {props.home.status.thermostat_livingroom.thermostatTemperatureAmbient} ºC
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
            props.home.status["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"].openPercent === 100 ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Ventana abierta
                    </div>
                </div>
            : <></>
        }
        {
            props.home.status.thermostat_livingroom.thermostatHumidityAmbient < 30 ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Humedad baja
                    </div>
                </div>
            : <></>
        }
        {
            props.home.status.thermostat_livingroom.thermostatHumidityAmbient > 55 ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Humedad alta
                    </div>
                </div>
            : <></>
        }
        {
            props.home.status["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"].openPercent === 0 && 
            props.home.status.thermostat_livingroom.thermostatMode === "cool" &&
            props.home.status.thermostat_livingroom.thermostatTemperatureAmbient > props.home.status.temperature_001.temperatureAmbientCelsius ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Abre la ventana
                    </div>
                </div>
            : <></>
        }
        {
            props.home.status["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"].openPercent === 100 && 
            props.home.status.scene_summer.enable &&
            props.home.status.thermostat_livingroom.thermostatMode === "off" &&
            props.home.status.thermostat_livingroom.thermostatTemperatureAmbient < props.home.status.temperature_001.temperatureAmbientCelsius ?
                <div className="homeCardRow">
                    <div className="roomCardAlertContainer">
                        Abre la ventana
                    </div>
                </div>
            : <></>
        }
    </div>
  )
}