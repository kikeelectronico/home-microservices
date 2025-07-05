import React, { useState, useEffect } from "react";
import "./power.css"

export default function Power(props) {

    const calcPower = () => {
        return (props.home.status.current001.brightness * 35)
    }

  return (
    <div className="homeCard" style={{boxShadow: "0 0.1rem 1rem rgba(" + (props.home.status.current001.brightness > 90 ? "255,0,0" : "0,0,0")  + ", 0.8)"}}>
        <div className="homeCardTitle">
            Potencia
        </div>
        <div className="roomCardRow">
            <div className="roomCardAmbientContainer">
                {calcPower()} W
            </div>
        </div>
        {
            props.home.status.current001.brightness > 90 ?
                <div className="roomCardRow">
                    <div className="roomCardAlertContainer">
                        Sobrecarga de potencia
                    </div>
                </div>
            : <></>
        }
    </div>
  )
}