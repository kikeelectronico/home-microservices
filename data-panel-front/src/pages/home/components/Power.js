import React from "react";
import "./power.css"

export default function Power(props) {

    const calcPower = () => {
        return (props.home.status.current001.brightness * 35)
    }

    return (
        <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + (props.home.status.current001.brightness > 90 ? "255,0,0" : "0,0,0")  + ", 0.8)"}}>
            <div className="homeCardTitle">
                Potencia
            </div>
            <div className="homeCardRow">
                <div className="powerCardPowerContainer">
                    {calcPower()} W
                </div>
            </div>
            {
                props.home.status.current001.brightness > 90 ?
                    <div className="homeCardRow">
                        <div className="powerCardAlertContainer">
                            Sobrecarga de potencia
                        </div>
                    </div>
                : <></>
            }
        </div>
    )
}