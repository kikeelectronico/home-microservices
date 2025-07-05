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
    <div className="outdoorCard">
        <div className="outdoorCardRow">
            <div className="outdoorCardColumn outdoorCardClockContainer">
                {time}
            </div>
            <div className="outdoorCardColumn outdoorCardWeatherContainer">
                <div className="outdoorCardWeatherRow">
                    <div className="outdoorCardWeatherTemperatureContainer">
                            {props.weather.temp_c} ºC
                        </div>
                    </div>
                <div className="outdoorCardWeatherRow">
                    <div className="outdoorCardWeatherSkyContainer">
                        <img className="outdoorCardWeatherSkyIcon" alt="f" src={props.weather.condition.icon}/>
                    </div>
                    <div className="outdoorCardWeatherUVindexContainer">
                        {props.weather.uv}
                    </div>
                    <div className="outdoorCardWeatherAQIContainer">
                        {props.weather.air_quality['us-epa-index']}
                    </div>
                </div>
            </div>
        </div>
        <div className="outdoorCardRow">
            <div className="outdoorCardWeatherRow">
                <div className="outdoorCardWindContainer">
                    {props.weather.wind_kph} km/h
                </div>
                <div className="outdoorCardWindContainer">
                    {props.weather.wind_dir}
                </div>
            </div>
        </div>
        {
            props.weather_alerts ? 
                props.weather_alerts.map((alert, index) => {

                    const getStyle = () => {
                        var style_name = "alertsCritical"
                        if (alert['severity'] === "normal") style_name = "alertsNormal"
                        else if (alert['severity'] === "high") style_name = "alertsHigh"
                        else if (alert['severity'] === "middle") style_name = "alertsMiddle"
                        else if (alert['severity'] === "low") style_name = "alertsLow"
                        return style_name
                    }
                    
                    return (
                        <div className="outdoorCardRow" key={index}>
                            <div className="outdoorCardWeatherRow">
                                <div className={"outdoorCardAlertContainer " +  getStyle()}>
                                    {alert.text}
                                </div>
                            </div>
                        </div>
                    )
                })
            : <></>
        }
    </div>
  )
}