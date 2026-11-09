import React from "react";
import "./room.css"

export default function Livingroom(props) {

    const thermostatMode = () => {
        var mode = props.home.thermostat_livingroom?.thermostatMode
        if (mode === "heat") return "Calefacción"
        if (mode === "cool") return "Aire acondicionado"
        if (mode === "fan-only") return "Ventilador"
        if (mode === "off") return ""
    }

    const thermostatColor = () => {
        if (props.home) {
            var mode = props.home.thermostat_livingroom?.thermostatMode
            if (mode === "heat" && props.home["fecf95fe-7cf3-4cc1-87bc-98e5669320f8_1"]?.on) return "255,0,0"
            else if (mode === "cool" && props.home.ac_001?.on) return "0,0,255"
            else if (mode === "fan-only" && props.home.ac_001?.on) return "255,255,255"
            else return "0,0,0"
        } else return "0,0,0"
    }

    const pm25AlertColor = (level) => {
        if (level > 85) return "alertsHigh"
        else if (level > 15) return "alertsMiddle"
        else return "alertsNormal"
    }

    return (
        <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + thermostatColor() + ", 0.8)"}}>
            <div className="homeCardTitle">
                Salón
            </div>
            <div className="homeCardRow" style={{marginTop: 5}}>
                <div className={"roomCardAmbientContainer " + (props.home?.thermostat_livingroom?.online ? "deviceOnline" : "deviceOffline")}>
                    {props.home?.thermostat_livingroom?.thermostatTemperatureAmbient ?? "--.-"} ºC
                </div>
            </div>
            {
                props.home ?
                <>
                {
                    thermostatMode() !== "" ?
                        <div className="homeCardRow alertAnimated homeCardRowNoBorder">
                            <div className="roomCardThermostatContainer deviceOnline">
                                {thermostatMode()}
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.home["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"]?.openPercent === 100 ?
                        <div className="homeCardRow alertAnimated">
                            <div className={"roomCardAlertContainer " + (props.home["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"]?.online ? "deviceOnline" : "deviceOffline")}>
                                Ventana abierta
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.home.thermostat_livingroom?.thermostatHumidityAmbient < 30 ?
                        <div className="homeCardRow alertAnimated">
                            <div className={"roomCardAlertContainer " + (props.home.thermostat_livingroom?.online ? "deviceOnline" : "deviceOffline")}>
                                Humedad baja
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.home.thermostat_livingroom?.thermostatHumidityAmbient > 55 ?
                        <div className="homeCardRow alertAnimated">
                            <div className={"roomCardAlertContainer " + (props.home.thermostat_livingroom?.online ? "deviceOnline" : "deviceOffline")}>
                                Humedad alta
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.home["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"]?.openPercent === 0 && 
                    props.home.thermostat_livingroom?.thermostatMode === "cool" &&
                    props.home.thermostat_livingroom?.thermostatTemperatureAmbient > props.home.temperature_001?.temperatureAmbientCelsius ?
                        <div className="homeCardRow alertAnimated">
                            <div className={"roomCardAlertContainer " + (props.home["e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4"]?.online ? "deviceOnline" : "deviceOffline")}>
                                Abre la ventana
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.home["df31ac85-be3f-48db-ab5e-483001f3ad27_1"]?.currentSensorStateData?.map(sensor => {
                    return sensor.name === "PM2.5" && sensor.rawValue > 5 ?
                            <div className="homeCardRow alertAnimated" key={sensor.name}>
                                <div className={"roomCardAlertContainer " + (sensor.rawValue  ? ("deviceOnline " + pm25AlertColor(sensor.rawValue)) : "deviceOffline")}>
                                    PM2.5: {sensor.rawValue} ppm
                                </div>
                            </div>
                        : <></>
                    })
                }
                </> : <></>
            }
        </div>
    )
}