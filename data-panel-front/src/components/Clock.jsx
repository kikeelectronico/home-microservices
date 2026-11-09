import React, { useState, useEffect } from "react";
import "./clock.css"

export default function Clock() {

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
    <div className="clockCard">
      <div className="clockTime">
        {time}
      </div>
    </div>
  )
}