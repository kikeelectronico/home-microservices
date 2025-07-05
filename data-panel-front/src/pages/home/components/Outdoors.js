import React, { useState, useEffect } from "react";
import "./outdoors.css"

export default function Outdoors(props) {

    const [time, setTime] = useState("11:20");

    useEffect(() => {
        updateTime();
        const interval = setInterval(() => updateTime(), 1000)

        return()=>clearInterval(interval)
    }, [])

    const updateTime = () => {
        var today = new Date()
        var hour = today.getHours()
        var minute = today.getMinutes()
        var time_string = (hour < 10 ? "0" + hour : hour) + ":" + (minute < 10 ? "0" + minute : minute)
        setTime(time_string)
    }

  return (
    <div className="homeCard">
        <div className="outdoorCardRow">
            <div className="outdoorCardColumn outdoorCardClockContainer">
                {time}
            </div>
            <div className="outdoorCardColumn outdoorCardWeatherContainer">
                <div className="outdoorCardWeatherRow">
                    <div className="outdoorCardWeatherTemperatureContainer">
                            {props.weather.current.temp_c} ºC
                        </div>
                    </div>
                <div className="outdoorCardWeatherRow">
                    <div className="outdoorCardWeatherSkyContainer">
                        <img className="outdoorCardWeatherSkyIcon" alt="f" src={props.weather.current.condition.icon}/>
                    </div>
                    <div className="outdoorCardWeatherUVindexContainer">
                        {props.weather.current.uv}
                    </div>
                    <div className="outdoorCardWeatherAQIContainer">
                        {props.weather.current.air_quality['us-epa-index']}
                    </div>
                </div>
            </div>
        </div>
        <div className="outdoorCardRow">
            <div className="outdoorCardWeatherRow">
                <div className="outdoorCardWindContainer">
                    {props.weather.current.wind_kph} km/h
                </div>
                <div className="outdoorCardWindContainer">
                    {props.weather.current.wind_dir}
                </div>
            </div>
        </div>
        {
            props.weather.alerts.alert ? 
                props.weather.alerts.alert.map((alert, index) => {

                    const getStyle = () => {
                        let severity = "alertsCritical"
                        if (alert.category.includes("Extreme")) severity = "alertsCritical"
                        else if (alert.event.includes("Moderate")) severity = "alertsMiddle"
                        else if (alert.event.includes("rojo")) severity = "alertsCritical"
                        else if (alert.event.includes("naranja")) severity = "alertsMiddle"
                        else if (alert.event.includes("amarillo")) severity = "alertsLow"
                        return severity
                    }
                    
                    return (
                        <div className="outdoorCardRow" key={index}>
                            <div className="outdoorCardWeatherRow">
                                <div className={"outdoorCardAlertContainer " +  getStyle()}>
                                    {alert.event + (alert.event[alert.event.length-1] !== "." ? "." : "") + (alert.desc !== "" ? " " + alert.desc : "") + (alert.desc[alert.desc.length-1] !== "." ? "." : "") + (alert.areas !== "" ? " " + alert.areas : "")}
                                </div>
                            </div>
                        </div>
                    )
                })
            : <></>
        }
        {
            props.water.water.level < 50 ? 
                <div className="outdoorCardRow">
                    <div className="outdoorCardWeatherRow">
                        <div className={"outdoorCardAlertContainer " +  (props.water.water.level < 40 ? "alertsLow" : "")}>
                            {"Nivel de embalses: " + props.water.water.level + " %"}
                        </div>
                    </div>
                </div>
            : <></>
        }
    </div>
  )
}