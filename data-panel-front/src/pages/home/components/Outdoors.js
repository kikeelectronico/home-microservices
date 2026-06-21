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
    <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")}>
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
            props.weather_warning ? 
                [...props.weather_warning]
                .sort((a, b) => {
                    if (a.is_active !== b.is_active) {
                        return a.is_active ? -1 : 1;
                    }

                    return a.start_offset - b.start_offset;
                })
                .map((alert, index) => {
                    if (alert.start_offset >= 0) {
                        const getStyle = () => {
                            let severity = "alertsNormal"
                            if (alert.level.includes("rojo")) severity = "alertsHigh"
                            else if (alert.level.includes("naranja")) severity = "alertsMiddle"
                            else if (alert.level.includes("amarillo")) severity = "alertsLow"
                            return severity
                        }
                        
                        return (
                            <div className="outdoorCardRow" key={index}>
                                <div className="outdoorCardWeatherRow">
                                    <div className={"outdoorCardAlertContainer " +  getStyle()}>
                                        {"(" + (alert.is_active ? "A" : alert.start_offset) + ") " + alert.title + " " + alert.description}
                                    </div>
                                </div>
                            </div>
                        )
                    }
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