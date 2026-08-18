import React from "react";
import "./power.css"

export default function Power(props) {

    const calcPower = () => {
        return props.home ? (props.home?.current001?.brightness * 35) : "----"
    }

    const shadowColor = () => {
        if (props.home?.current001?.brightness > 100) return "255,0,0"
        else if (props.home?.current001?.brightness > 90) return "255,165,0"
        else return "0,0,0"
    }

    return (
        <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")} style={{boxShadow: "0 0.1rem 1rem rgba(" + shadowColor()  + ", 0.8)"}}>
            <div className="homeCardTitle">
                Potencia
            </div>
            <div className="homeCardRow">
                <div className={"powerCardPowerContainer " + (props.home?.current001?.online ? "deviceOnline" : "deviceOffline")}>
                    {calcPower()} W
                </div>
            </div>
            {
                props.home?.current001?.brightness > 100 ?
                    <div className="homeCardRow">
                        <div className={"powerCardAlertContainer " + (props.home?.current001?.online ? "deviceOnline" : "deviceOffline")}>
                            Sobrecarga de potencia
                        </div>
                    </div>
                : <></>
            }
        </div>
    )
}