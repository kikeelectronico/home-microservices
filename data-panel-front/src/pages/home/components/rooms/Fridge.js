import React from "react";
import "./room.css"

export default function Fridge(props) {

  return (
    <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(0,0,0, 0.8)"}}>
        <div className="homeCardTitle">
            Nevera
        </div>
        <div className="homeCardRow" style={{marginTop: 5}}>
            <div className="roomCardAmbientContainer">
                {props.home.status.temperature_001.temperatureAmbientCelsius} ºC
            </div>
        </div>
    </div>
  )
}