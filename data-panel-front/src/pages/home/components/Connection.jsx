import React from "react";
import "./connection.css"

export default function Connection(props) {

    return (
        (!props.internet.connected) || props.see_closed ? 
            <div className={"homeCard" + (props.playing ? " homeCardAlphaChannel" : "")}>
                <div className="homeCardTitle">
                    Conectividad
                </div>
                {
                    !props.internet.connected ?
                        <div className="homeCardRow">
                            <div className="connectionCardAlertContainer">
                                Sin conexión a Internet
                            </div>
                        </div>
                    : <></>
                }
                {
                    props.see_closed ?
                        <div className="homeCardRow">
                            <div className="connectionCardAlertContainer">
                                Sin conexión con la API
                            </div>
                        </div>
                    : <></>
                }
            </div>
        : <></>
    )
}